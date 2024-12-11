from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from wellness.filters import CaseInsensitiveSearchFilter
from wellness.models import Article, Test, Answer, Result
from wellness.pagination import ArticlePagination, TestPagination
from wellness.serializers import ArticleSerializer, TestSerializer, ArticleNestedSerializer, TestSubmissionSerializer, \
    TestListSerializer, ResultSerializer


class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    filter_backends = [CaseInsensitiveSearchFilter]
    pagination_class = ArticlePagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleNestedSerializer
        return ArticleSerializer


class TestViewSet(ModelViewSet):
    serializer_class = TestSerializer
    queryset = Test.objects.all()
    lookup_field = "slug"
    filter_backends = [CaseInsensitiveSearchFilter]
    pagination_class = TestPagination

    def retrieve(self, request, slug=None):
        try:
            test = Test.objects.get(slug=slug)
            serializer = TestSerializer(test, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({"detail": "Тест не найден"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=TestSubmissionSerializer,
    )
    def check(self, request):
        try:
            test = Test.objects.get(slug=request.data.get('test_slug', ''))
        except Test.DoesNotExist:
            return Response({"detail": "Тест не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if test.test_type != 2:
            selected_answers = serializer.validated_data['answers']
        else:
            colors_order = [1, 2, 3, 4, 5, 6, 7, 8]
            answers_colors = serializer.validated_data['answers_colors']
            first_choice = answers_colors[0]
            second_choice = answers_colors[1]

            color_scores = {}

            for i, color_data in enumerate(first_choice + second_choice):
                color_id = color_data['answer_id']
                color_points = color_data['points']

                if color_id not in color_scores:
                    color_scores[color_id] = 0
                color_scores[color_id] += color_points

            CO = sum(
                abs(color_scores.get(color, 0) - color_data['points']) for color, color_data in colors_order.items())

            VK = (18 - color_scores.get(3, 0) - color_scores.get(7, 0)) / (
                        18 - color_scores.get(5, 0) - color_scores.get(1, 0))

            anxiety_score = 0
            for color1, color2 in zip(first_choice, second_choice):
                anxiety_score += abs(color1['answer_id'] - color2['answer_id'])
            result = Result.objects.filter(test=test).first()

            return Response({
                "description": result.description,
                "test_name": test.title,
                "image": f"{settings.CURRENT_DOMAIN}{result.test.full_image.url}",
                "vegetative": VK,
                "deviation": CO,
                "anxiety": anxiety_score
            }, status=HTTP_200_OK)
        from collections import Counter
        answer_counts = Counter(selected_answers)

        answer_objects = Answer.objects.filter(id__in=answer_counts.keys())
        if test.test_type == 3:
            result = Result.objects.filter(test=test).first()
            if result is not None:
                serialized = ResultSerializer(result)
                return Response(data=serialized.data)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        if test.calculation == "point":
            total_points = sum(
                getattr(answer, 'points', 1) * answer_counts[answer.id] for answer in answer_objects
            )
            result = Result.objects.filter(
                test=test,
                min_points__lte=total_points,
                max_points__gte=total_points
            ).first()

        elif test.calculation == "position":
            positions = [i + 1 for i, answer in enumerate(selected_answers)]
            position_sum = sum(positions)
            result = Result.objects.filter(
                test=test,
                position__gte=position_sum
            ).order_by('position').first()

        else:
            return Response({"detail": "Метод подсчёта не поддерживается"}, status=status.HTTP_400_BAD_REQUEST)

        if result:
            return Response({
                "description": result.description,
                "test_name": result.test.title,
                "image": f"{settings.CURRENT_DOMAIN}{result.test.full_image.url}",
                "details": {
                    "total_points": total_points if test.calculation == "point" else None,
                    "position_sum": position_sum if test.calculation == "position" else None,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Результат не определён"}, status=status.HTTP_400_BAD_REQUEST)


class TestListAPIView(ListAPIView):
    queryset = Test.objects.all()[:5]
    serializer_class = TestListSerializer
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
        if test.type != 3:
            selected_answers = serializer.validated_data['answers']
        else:
            selected_answers = serializer.validated_data['colors']
            return Response({
                "vegetative": 1,
                "deviation": 1,
                "anxiety": 1
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
from collections import defaultdict

from celery.bin.result import result
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from wellness.filters import CaseInsensitiveSearchFilter
from wellness.models import Article, Test, Answer, Result, Question
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
            answers_colors = serializer.validated_data['answers_colors']
            first_choice = answers_colors[0]
            second_choice = answers_colors[1]

            color_scores = {}

            for choice_group in [first_choice, second_choice]:
                for color_data in choice_group:
                    color_id = color_data['id']

                    try:
                        answer = Answer.objects.get(id=color_id)
                        color_points = answer.points
                        ideal_points = answer.ideal_score
                    except Answer.DoesNotExist:
                        color_points, ideal_points = 0, 0

                    if color_id not in color_scores:
                        color_scores[color_id] = 0
                    color_scores[color_id] = {'points': color_points, 'ideal_score': ideal_points}

                CO = 0
                for color_id, scores in color_scores.items():
                    CO += abs(scores['points'] - scores['ideal_score'])
            VK = (18 - color_scores.get(3, {'points': 0})['points'] - color_scores.get(7, {'points': 0})['points']) / \
                 (18 - color_scores.get(5, {'points': 0})['points'] - color_scores.get(1, {'points': 0})['points'])

            anxiety_score = 0
            for color1, color2 in zip(first_choice, second_choice):
                anxiety_score += abs(color1['id'] - color2['id'])
            result = Result.objects.filter(test=test).first()

            return Response({
                "description": result.description,
                "test_name": test.title,
                "image": f"{settings.CURRENT_DOMAIN}{result.test.full_image.url}",
                "vegetative": round(VK, 2),
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

        if test.test_type == 4:
            selected_answers = serializer.validated_data['answers']
            answers = Answer.objects.filter(id__in=selected_answers).prefetch_related("question_set")
            result = Result.objects.filter(test=test).first()
            scale_scores = defaultdict(lambda: {"score": 0, "min": 0, "max": 0})

            for answer in answers:

                for question in answer.question_set.all():

                    scale_name = question.scale
                    scale_scores[scale_name]["score"] += answer.points

            all_questions = Question.objects.filter(tests=test).prefetch_related("answers")

            for question in all_questions:
                scale_name = question.scale
                possible_points = [ans.points for ans in question.answers.all()]

                if possible_points:
                    scale_scores[scale_name]["min"] += min(possible_points)
                    scale_scores[scale_name]["max"] += max(possible_points)

            return Response(data={"score": scale_scores, "result": result.description}, status=status.HTTP_200_OK)

        if test.test_type == 5:
            result = Result.objects.filter(test=test).first()
            base_description = result.description

            user_answers = Answer.objects.filter(id__in=selected_answers)
            user_answers_text = "\n".join([answer.description for answer in user_answers])

            final_description = f"{base_description}\n\nОтветы пользователя:\n{user_answers_text}"

            return Response({
                "description": final_description,
                "test_name": test.title,
                "image": f"{settings.CURRENT_DOMAIN}{result.test.full_image.url}",
            }, status=status.HTTP_200_OK)
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
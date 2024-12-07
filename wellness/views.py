from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from wellness.filters import CaseInsensitiveSearchFilter
from wellness.models import Article, Test, Answer, Result
from wellness.pagination import ArticlePagination, TestPagination
from wellness.serializers import ArticleSerializer, TestSerializer, ArticleNestedSerializer, TestSubmissionSerializer


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

    def retrieve(self, request, pk=None):
        try:
            test = Test.objects.get(id=pk)
            serializer = TestSerializer(test)
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

        selected_answers = serializer.validated_data['answers']
        answers = Answer.objects.filter(id__in=selected_answers)

        if test.calculation == "point":
            total_points = sum(getattr(answer, 'points', 1) for answer in answers)
            result = Result.objects.filter(
                test=test,
                min_points__lte=total_points,
                max_points__gte=total_points
            ).first()

        elif test.calculation == "position":
            positions = [i + 1 for i, answer in enumerate(answers)]
            position_sum = sum(positions)
            result = Result.objects.filter(
                test=test,
                position__gte=position_sum
            ).order_by('position').first()

        else:
            return Response({"detail": "Метод подсчёта не поддерживается"}, status=status.HTTP_400_BAD_REQUEST)

        if result:
            return Response({
                "result": result.description,
                "details": {
                    "total_points": total_points if test.calculation == "point" else None,
                    "position_sum": position_sum if test.calculation == "position" else None,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Результат не определён"}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from wellness.models import Article, Test
from wellness.pagination import ArticlePagination
from wellness.serializers import ArticleSerializer, TestSerializer, ArticleNestedSerializer


class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['title']
    pagination_class = ArticlePagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleNestedSerializer
        return ArticleSerializer

class TestViewSet(ModelViewSet):
    serializer_class = TestSerializer
    queryset = Test.objects.all()
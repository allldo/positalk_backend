from rest_framework.viewsets import ModelViewSet

from wellness.models import Article, Test
from wellness.serializers import ArticleSerializer, TestSerializer


class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    queryset = Article.objects.all()


class TestViewSet(ModelViewSet):
    serializer_class = TestSerializer
    queryset = Test.objects.all()
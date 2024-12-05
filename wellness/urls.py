from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wellness.views import ArticleViewSet, TestViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tests', TestViewSet, basename='test')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wellness.views import ArticleViewSet, TestViewSet, TestListAPIView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tests', TestViewSet, basename='test')

urlpatterns = [
    path('tests/check/', TestViewSet.as_view({'post': 'check'})),
    path('tests/recommended/', TestListAPIView.as_view()),
] + router.urls

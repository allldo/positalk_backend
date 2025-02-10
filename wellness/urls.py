from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wellness.views import ArticleViewSet, TestViewSet, TestListAPIView, AbuseAPIView, GetAnswers

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tests', TestViewSet, basename='test')

urlpatterns = [
    path('tests/check/', TestViewSet.as_view({'post': 'check'})),
    path('tests/recommended/', TestListAPIView.as_view()),

    path('get-last-answers/', GetAnswers.as_view()),
    path('abuse/', AbuseAPIView.as_view())
] + router.urls

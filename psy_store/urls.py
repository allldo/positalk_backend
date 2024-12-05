from django.urls import path

from psy_store.views import GiftSessionListAPIView

urlpatterns = [
    path('', GiftSessionListAPIView.as_view()),
]

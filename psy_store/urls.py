from django.urls import path

from psy_store.views import GiftSessionListAPIView, PsychologistsListAPIView

urlpatterns = [
    path('gifts-list/', GiftSessionListAPIView.as_view()),
    path('psychologists/', PsychologistsListAPIView.as_view()),
]

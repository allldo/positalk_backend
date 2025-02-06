from django.urls import path
from rest_framework.routers import DefaultRouter

from session.views import PsychologistSessionListAPIView, TimeSlotViewSet, PsychologistScheduleRangeAPIView

router = DefaultRouter()
router.register(r'timeslots', TimeSlotViewSet, basename='timeslot')
urlpatterns = [
    path('psychologists-list/', PsychologistSessionListAPIView.as_view()),
    path('schedule/<int:psychologist_id>/', PsychologistScheduleRangeAPIView.as_view(), name='psychologist_schedule'),

    # path('verify-webhook/', WebhookVerifyView.as_view(), name='verify_webhook'),
] + router.urls
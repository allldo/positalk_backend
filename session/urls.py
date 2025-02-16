from django.urls import path
from rest_framework.routers import DefaultRouter

from session.views import PsychologistSessionListAPIView, TimeSlotViewSet, PsychologistScheduleRangeAPIView, \
    TransferSessionAPIView, CancelSessionAPIView, BookSessionAPIView, MyScheduleRangeAPIView, MyClientsListAPIView, \
    MyBusyScheduleRangeAPIView, ClientHasAPIView

router = DefaultRouter()
router.register(r'timeslots', TimeSlotViewSet, basename='timeslot')
urlpatterns = [
    path('psychologists-list/', PsychologistSessionListAPIView.as_view(), name='psychologist_list'),
    path('schedule/<int:psychologist_id>/', PsychologistScheduleRangeAPIView.as_view(), name='psychologist_schedule'),

    path('has_schedule/', ClientHasAPIView.as_view(), name='has_schedule'),

    path('my_schedule/', MyScheduleRangeAPIView.as_view(), name='my_schedule'),
    path('my_client/', MyClientsListAPIView.as_view(), name='my_clients'),
    path('my_schedule/busy/', MyBusyScheduleRangeAPIView.as_view(), name='busy_schedule'),

    path('transfer/<int:session_id>/', TransferSessionAPIView.as_view(), name='transfer_session'),
    path('cancel/<int:session_id>/', CancelSessionAPIView.as_view(), name='cancel_session'),
    path('book/<int:psychologist_id>/', BookSessionAPIView.as_view(), name='book_session'),
    # path('verify-webhook/', WebhookVerifyView.as_view(), name='verify_webhook'),
] + router.urls
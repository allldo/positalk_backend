from django.urls import path

from sales.views import LinkPaymentAPIView, WebhookVerifyView

urlpatterns = [
    path('payment-link/', LinkPaymentAPIView.as_view()),
    path('verify-webhook/', WebhookVerifyView.as_view(), name='verify_webhook'),
]
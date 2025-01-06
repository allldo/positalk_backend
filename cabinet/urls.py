from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import SendCodeView, VerifyCodeView, SurveyInfoView, SurveySubmitView

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('send-code/', SendCodeView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('survey-info/', SurveyInfoView.as_view(), name='survey-info'),
    path('survey/', SurveySubmitView.as_view(), name='survey-info')
]
from django.urls import path

from .views import SendCodeView, VerifyCodeView, SurveyInfoView, SurveySubmitView

urlpatterns = [
    path('send-code/', SendCodeView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('survey-info/', SurveyInfoView.as_view(), name='survey-info'),
    path('survey/', SurveySubmitView.as_view(), name='survey-info')
]
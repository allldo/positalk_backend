from django.urls import path

from .views import SendCodeView, VerifyCodeView, SurveyInfoView, SurveySubmitView, ApplySurveyPsychologist, \
    PsychologistSurveyUpdateView

urlpatterns = [
    path('send-code/', SendCodeView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('survey-info/', SurveyInfoView.as_view(), name='survey-info'),
    path('survey/', SurveySubmitView.as_view(), name='survey-info'),
    path('apply-psychologist-survey/', ApplySurveyPsychologist.as_view()),

    path('change-self-psychologist/', PsychologistSurveyUpdateView.as_view())
]
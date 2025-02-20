from django.urls import path

from .views import SendCodeView, VerifyCodeView, SurveyInfoView, SurveySubmitView, ApplySurveyPsychologist, \
    PsychologistSurveyUpdateView, PsychologistSurveyGetView, PsychologistSurveyCreateAPIView, AdjustScheduleAPIView \
    , GetSelfUserView, PsychologistEducationView

urlpatterns = [
    path('send-code/', SendCodeView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('survey-info/', SurveyInfoView.as_view(), name='survey-info'),
    path('survey/', SurveySubmitView.as_view(), name='survey-info'),
    path('apply-psychologist-survey/', ApplySurveyPsychologist.as_view()),

    path('self/', GetSelfUserView.as_view()),

    path('create-self-psychologist/', PsychologistSurveyCreateAPIView.as_view()),
    path('change-self-psychologist/', PsychologistSurveyUpdateView.as_view()),
    path('self-psychologist/', PsychologistSurveyGetView.as_view()),

    path('psychologist_education/', PsychologistEducationView.as_view()),
    path('adjust-schedule/', AdjustScheduleAPIView.as_view()),
]
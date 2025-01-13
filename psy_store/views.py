from itertools import chain

from django.db.models import Prefetch
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from cabinet.models import PsychologistSurvey, Survey
from psy_store.models import GiftSession
from psy_store.serializers import GiftSessionSerializer, PsychologistsSurveySerializer


class GiftSessionListAPIView(ListAPIView):
    serializer_class = GiftSessionSerializer
    queryset = GiftSession.objects.all()


class PsychologistsListAPIView(ListAPIView):
    serializer_class = PsychologistsSurveySerializer
    queryset = PsychologistSurvey.objects.prefetch_related('psycho_topic')
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user

        user_survey = user.profile.first()
        user_survey = Survey.objects.prefetch_related(
            Prefetch('feeling'),
            Prefetch('relation'),
            Prefetch('work_study'),
            Prefetch('life_event'),
            Prefetch('couple_therapy'),
        ).get(id=user_survey.id)

        user_topics = set(
            chain(
                user_survey.feeling.all().values_list('name', flat=True),
                user_survey.relation.all().values_list('name', flat=True),
                user_survey.work_study.all().values_list('name', flat=True),
                user_survey.life_event.all().values_list('name', flat=True),
                user_survey.couple_therapy.all().values_list('name', flat=True),
            )
        )

        if not user_topics:
            return PsychologistSurvey.objects.none()

        gender = self.request.query_params.get('gender')
        age_min = self.request.query_params.get('age_min')
        age_max = self.request.query_params.get('age_max')
        queryset = PsychologistSurvey.objects.filter(
            psycho_topic__name__in=user_topics
        ).distinct()

        if gender:
            queryset = queryset.filter(gender=gender)

        if age_min:
            queryset = queryset.filter(age__gte=int(age_min))

        if age_max:
            queryset = queryset.filter(age__lte=int(age_max))

        return queryset
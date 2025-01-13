from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from cabinet.models import PsychologistSurvey, Education
from psy_store.models import GiftSession


class GiftSessionSerializer(ModelSerializer):
    class Meta:
        model = GiftSession
        fields = "__all__"


class EducationSerializer(ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'year', 'text']

class PsychologistsSurveySerializer(ModelSerializer):
    psycho_topic = StringRelatedField(many=True)
    education_psychologist = EducationSerializer(many=False)

    class Meta:
        model = PsychologistSurvey
        fields = "__all__"
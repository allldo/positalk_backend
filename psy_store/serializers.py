from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from cabinet.models import PsychologistSurvey
from psy_store.models import GiftSession


class GiftSessionSerializer(ModelSerializer):
    class Meta:
        model = GiftSession
        fields = "__all__"


class PsychologistsSurveySerializer(ModelSerializer):
    psycho_topic = StringRelatedField(many=True)

    class Meta:
        model = PsychologistSurvey
        fields = "__all__"
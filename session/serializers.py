from rest_framework.fields import DateTimeField
from rest_framework.serializers import ModelSerializer

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot


class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'day_of_week', 'time', 'is_available']
        read_only_fields = ['id', 'is_available']


class PsychologistSessionSerializer(ModelSerializer):
    last_session = DateTimeField(read_only=True)
    next_session = DateTimeField(read_only=True)

    class Meta:
        model = PsychologistSurvey
        fields = ['id', 'name', 'last_session', 'next_session']

from rest_framework.fields import DateTimeField, SerializerMethodField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot, Session


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
        fields = ['id', 'name','photo', 'last_session', 'next_session']


class SessionDateSerializer(Serializer):
    start_time = DateTimeField()
    end_time = DateTimeField()


class PsychologistClientSerializer(ModelSerializer):
    client_nickname = SerializerMethodField()
    client_avatar = SerializerMethodField()
    session_count = IntegerField(read_only=True)
    last_session_date = DateTimeField(format="%Y-%m-%d %H:%M", allow_null=True)
    future_session_date = DateTimeField(format="%Y-%m-%d %H:%M", allow_null=True)

    class Meta:
        model = PsychologistSurvey
        fields = [
            'client_nickname',
            'client_avatar',
            'session_count',
            'last_session_date',
            'future_session_date'
        ]

    def get_client_nickname(self, obj):
        return obj.user.get_name()

    def get_client_avatar(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url)
        return None

from django.db.models import Model
from rest_framework.fields import DateTimeField, SerializerMethodField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot, Session, Chat, Message


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


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created_at']


class ChatPsychologistSerializer(ModelSerializer):
    client_nickname = SerializerMethodField()
    # client_avatar = SerializerMethodField()
    last_message = SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id',
            'client_nickname',
            'last_message',
        ]

    def get_client_nickname(self, obj):
        return obj.client.get_name()

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data


class ChatClientSerializer(ModelSerializer):
    psychologist_nickname = SerializerMethodField()
    psychologist_avatar = SerializerMethodField()
    last_message = SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id',
            'psychologist_nickname',
            'psychologist_avatar',
            'last_message',
        ]

    def get_psychologist_nickname(self, obj):
        return obj.psychologist.get_psychologist_name()

    def get_psychologist_avatar(self, obj):
        return obj.psychologist.get_psychologist_avatar()


    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
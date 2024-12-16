from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class PhoneSerializer(Serializer):
    phone = CharField(max_length=15)

class CodeVerificationSerializer(Serializer):
    phone = CharField(max_length=15)
    code = CharField(max_length=6)
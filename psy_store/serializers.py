from rest_framework.serializers import ModelSerializer

from psy_store.models import GiftSession


class GiftSessionSerializer(ModelSerializer):
    class Meta:
        model = GiftSession
        fields = "__all__"
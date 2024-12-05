from rest_framework.generics import ListAPIView

from psy_store.models import GiftSession
from psy_store.serializers import GiftSessionSerializer


class GiftSessionListAPIView(ListAPIView):
    serializer_class = GiftSessionSerializer
    queryset = GiftSession.objects.all()

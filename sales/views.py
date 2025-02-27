import hashlib
import hmac
import json

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from sales.serializers import LinkPaymentSerializer


class LinkPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @extend_schema(request=LinkPaymentSerializer)
    def post(self, request):
        serialized = LinkPaymentSerializer(data=request.data)
        if serialized.is_valid():
            try:
                link_data = serialized.save()
                return Response(link_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class WebhookVerifyView(APIView):
    def post(self, request):
        payload = request.POST.dict()
        sign = request.headers.get('Sign')

        secret_key = settings.PAYFORM_SECRET_KEY

        sorted_data = self.sort(payload)

        generated_signature = self.create_signature(sorted_data, secret_key)

        if self.verify_signature(generated_signature, sign):
            return Response({"status": "success", "message": "Webhook verified successfully."}, status=200)
        else:
            return Response({"error": "Invalid signature."}, status=400)

    def sort(self, data):
        if isinstance(data, dict):
            return {k: self.sort(v) for k, v in sorted(data.items())}
        elif isinstance(data, list):
            return [self.sort(item) for item in data]
        else:
            return str(data)

    def create_signature(self, data, key):
        data_json = json.dumps(data, ensure_ascii=False)
        return hmac.new(key.encode('utf-8'), data_json.encode('utf-8'), hashlib.sha256).hexdigest()

    def verify_signature(self, generated_signature, received_signature):
        return generated_signature == received_signature
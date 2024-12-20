from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from cabinet.models import PhoneVerification
from cabinet.serializers import PhoneSerializer, CodeVerificationSerializer
from cabinet.services import send_sms

User = get_user_model()

class SendCodeView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = PhoneVerification.generate_code()

        PhoneVerification.objects.create(phone=phone, code=code)
        send_sms(phone, code)
        return Response({"message": code}, status=status.HTTP_200_OK)
        # return Response({"message": "Код отправлен!"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = CodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            verification = PhoneVerification.objects.filter(phone=phone, code=code, is_active=True).latest('created_at')
            if not verification.is_valid():
                return Response({"error": "Код истёк"}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneVerification.DoesNotExist:
            return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone)
        verification.is_active = False
        verification.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "phone": user.phone_number,
            }
        }, status=status.HTTP_200_OK)

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cabinet.models import PhoneVerification, PsychologistSurvey
from cabinet.serializers import PhoneSerializer, CodeVerificationSerializer, SurveyInfoSerializer, \
    SurveySubmitSerializer
from cabinet.services import send_sms
from psy_store.serializers import PsychologistsSurveySerializer
from session.permissions import IsPsychologist
from wellness.models import Feeling, Relation, WorkStudy, LifeEvent, CoupleTherapy, PreferablePrice

User = get_user_model()

class SendCodeView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = PhoneVerification.generate_code()
        PhoneVerification.objects.filter(phone=phone).update(is_active=False)
        PhoneVerification.objects.create(phone=phone, code=code)
        # send_sms(phone, code)
        return Response({"message": code}, status=status.HTTP_200_OK)
        # return Response({"message": "Код отправлен!"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = CodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        is_psychologist = serializer.validated_data['is_psychologist']

        try:
            verification = PhoneVerification.objects.filter(phone=phone, code=code, is_active=True).latest('created_at')
            if not verification.is_valid():
                return Response({"error": "Код истёк"}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneVerification.DoesNotExist:
            return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone, user_type='psychologist' if is_psychologist else 'user')
        verification.is_active = False
        verification.save()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": str(token),
            "user": {
                "id": user.id,
                "phone": user.phone_number,
                "has_survey": user.profile.exists(),
                "user_type": user.user_type
            }
        }, status=status.HTTP_200_OK)


class SurveyInfoView(APIView):
    def get(self, request):
        data = {
            "feeling": Feeling.objects.all(),
            "relation": Relation.objects.all(),
            "work_study": WorkStudy.objects.all(),
            "life_event": LifeEvent.objects.all(),
            "couple_therapy": CoupleTherapy.objects.all(),
            "preferable_price": PreferablePrice.objects.all(),
        }
        serializer = SurveyInfoSerializer(data)
        return Response(serializer.data, status=200)


class SurveySubmitView(CreateAPIView):
    serializer_class = SurveySubmitSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = SurveySubmitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            survey = serializer.save()
            return Response(SurveySubmitSerializer(survey).data, status=201)
        return Response(serializer.errors, status=400)


class ApplySurveyPsychologist(CreateAPIView):
    serializer_class = PsychologistsSurveySerializer
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        survey = serializer.save()
        return Response(self.get_serializer(survey).data, status=201)


class PsychologistSurveyUpdateView(UpdateAPIView):
    serializer_class = PsychologistsSurveySerializer
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        return PsychologistSurvey.objects.get(user_id=self.request.user.id)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = serializer.instance
        instance.is_approved = False
        instance.save()


class PsychologistSurveyGetView(RetrieveAPIView):
    serializer_class = PsychologistsSurveySerializer
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        return PsychologistSurvey.objects.get(user_id=self.request.user.id)


class PsychologistSurveyCreateAPIView(CreateAPIView):
    serializer_class = PsychologistsSurveySerializer
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

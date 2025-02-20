from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cabinet.models import PhoneVerification, PsychologistSurvey, Education
from cabinet.serializers import PhoneSerializer, CodeVerificationSerializer, SurveyInfoSerializer, \
    SurveySubmitSerializer, SelfSerializer
from cabinet.services import send_sms, adjust_time_slot, validate_phone_number
from psy_store.serializers import PsychologistsSurveySerializer, EducationSerializer
from session.models import TimeSlot
from session.permissions import IsPsychologist
from wellness.models import Feeling, Relation, WorkStudy, LifeEvent, CoupleTherapy, PreferablePrice

User = get_user_model()

class SendCodeView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            phone = validate_phone_number(serializer.validated_data['phone'])
        except ValidationError as e:
            return Response({"error": e}, status=400)
        code = PhoneVerification.generate_code()
        PhoneVerification.objects.filter(phone=phone).update(is_active=False)
        PhoneVerification.objects.create(phone=phone, code=code)
        # send_sms(phone, code)
        return Response({"message": code}, status=200)
        # return Response({"message": "Код отправлен!"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = CodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            phone = validate_phone_number(serializer.validated_data['phone'])
        except ValidationError as e:
            return Response({"error": e}, status=400)
        code = serializer.validated_data['code']
        is_psychologist = serializer.validated_data['is_psychologist']

        try:
            verification = PhoneVerification.objects.filter(phone=phone, code=code, is_active=True).latest('created_at')
            if not verification.is_valid():
                return Response({"error": "Код истёк"}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneVerification.DoesNotExist:
            return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone)
        verification.is_active = False
        verification.save()
        if is_psychologist and created:
            user.user_type = 'psychologist'
            user.save()
            PsychologistSurvey.objects.create(
                user=user
            )
        if not is_psychologist and created:
            user.user_type = 'user'
            user.save()

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
        serializer.save(request=self.request)

        instance = serializer.instance
        instance.is_approved = False
        instance.save()

    def perform_create(self, serializer):
        serializer.save(request=self.request)

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


class AdjustScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        psychologist = request.user.get_psychologist()
        adjust_time_slot(psychologist, request.data)
        # results = []
        #
        # for time_slot_data in request.data:
        #     result = adjust_time_slot(psychologist, time_slot_data)
        #     results.append(result)

        return Response(data={"status": "success"}, status=200)


class GetSelfUserView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = self.request.user
        return Response(data=SelfSerializer(user).data, status=200)


class PsychologistEducationView(ListCreateAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        educations = []
        for key in request.data:
            if key.startswith("education["):
                index = key.split("[")[1].split("]")[0]
                field_name = key.split("][")[1][:-1]

                while len(educations) <= int(index):
                    educations.append({})

                educations[int(index)][field_name] = request.data[key]

        serializer = self.get_serializer(data=educations, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
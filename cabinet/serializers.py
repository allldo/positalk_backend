from datetime import date

from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, SerializerMethodField, BooleanField
from rest_framework.serializers import Serializer, ModelSerializer

from cabinet.models import Survey, CustomUser
from session.models import Connection
from session.serializers import ConnectionSerializer
from wellness.models import Feeling, Relation, WorkStudy, LifeEvent, CoupleTherapy, PreferablePrice


class PhoneSerializer(Serializer):
    phone = CharField(max_length=30)


class CodeVerificationSerializer(Serializer):
    phone = CharField(max_length=30)
    code = CharField(max_length=6)
    is_psychologist = BooleanField(default=False)


class FeelingSerializer(ModelSerializer):
    class Meta:
        model = Feeling
        fields = ['id', 'name']


class RelationSerializer(ModelSerializer):
    class Meta:
        model = Relation
        fields = ['id', 'name']


class WorkStudySerializer(ModelSerializer):
    class Meta:
        model = WorkStudy
        fields = ['id', 'name']


class LifeEventSerializer(ModelSerializer):
    class Meta:
        model = LifeEvent
        fields = ['id', 'name']


class CoupleTherapySerializer(ModelSerializer):
    class Meta:
        model = CoupleTherapy
        fields = ['id', 'name']


class PreferablePriceSerializer(ModelSerializer):
    class Meta:
        model = PreferablePrice
        fields = ['id', 'price', 'experience', 'description', 'specialists_num', 'therapy_type']


class SurveyInfoSerializer(Serializer):
    feeling = FeelingSerializer(many=True, read_only=True)
    relation = RelationSerializer(many=True, read_only=True)
    work_study = WorkStudySerializer(many=True, read_only=True)
    life_event = LifeEventSerializer(many=True, read_only=True)
    couple_therapy = CoupleTherapySerializer(many=True, read_only=True)
    preferable_price = PreferablePriceSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        return {
            "feeling": FeelingSerializer(instance.get("feeling"), many=True).data,
            "relation": RelationSerializer(instance.get("relation"), many=True).data,
            "work_study": WorkStudySerializer(instance.get("work_study"), many=True).data,
            "life_event": LifeEventSerializer(instance.get("life_event"), many=True).data,
            "couple_therapy": CoupleTherapySerializer(instance.get("couple_therapy"), many=True).data,
            "preferable_price": PreferablePriceSerializer(instance.get("preferable_price"), many=True).data,
        }


class SurveySubmitSerializer(ModelSerializer):
    class Meta:
        model = Survey
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user

        feeling_data = validated_data.pop('feeling', None)
        relation_data = validated_data.pop('relation', None)
        work_study_data = validated_data.pop('work_study', None)
        life_event_data = validated_data.pop('life_event', None)
        couple_therapy_data = validated_data.pop('couple_therapy', None)
        survey_exists = Survey.objects.filter(user=user)
        if survey_exists.exists():
            return survey_exists.last()

        survey = Survey.objects.create(user=user, **validated_data)

        if feeling_data:
            survey.feeling.set(feeling_data)
        if relation_data:
            survey.relation.set(relation_data)
        if work_study_data:
            survey.work_study.set(work_study_data)
        if life_event_data:
            survey.life_event.set(life_event_data)
        if couple_therapy_data:
            survey.couple_therapy.set(couple_therapy_data)

        return survey

    def validate_date_of_birth(self, date_of_birth):
        today = date.today()
        if date_of_birth > today:
            raise ValidationError("Date of birth cannot be in the future.")
        if today.year - date_of_birth.year > 100:
            raise ValidationError("Date of birth cannot be more than 100 years ago.")
        return date_of_birth


class SelfSerializer(ModelSerializer):

    has_survey = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'user_type', 'phone_number', 'has_survey']

    def get_has_survey(self, obj):
        return Survey.objects.filter(user=obj).exists()


class SelfClientSurveySerializer(ModelSerializer):
    phone = CharField(source='user.phone_number',max_length=45, read_only=True)
    psychologists = SerializerMethodField()

    class Meta:
        model = Survey
        exclude = ['user']

    def get_psychologists(self, obj):

        return ConnectionSerializer(Connection.objects.filter(client=obj, is_active=True), many=True).data

    def update(self, instance, validated_data):
        email = validated_data.get('email')
        if email or email == "":
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Invalid email address")

            if Survey.objects.filter(email=email).exclude(id=instance.id).exists():
                raise ValidationError("This email already exists")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
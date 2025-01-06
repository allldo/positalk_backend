from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer

from cabinet.models import Survey
from wellness.models import Feeling, Relation, WorkStudy, LifeEvent, CoupleTherapy, PreferablePrice


class PhoneSerializer(Serializer):
    phone = CharField(max_length=15)

class CodeVerificationSerializer(Serializer):
    phone = CharField(max_length=15)
    code = CharField(max_length=6)


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
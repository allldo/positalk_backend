import json

from jsonschema.exceptions import ValidationError
from rest_framework.fields import DecimalField, ListField, CharField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from cabinet.models import PsychologistSurvey, Education, CustomUser
from psy_store.models import GiftSession
from wellness.models import PsychoTopic
from wellness.serializers import PsychoTopicSerializer


class GiftSessionSerializer(ModelSerializer):
    class Meta:
        model = GiftSession
        fields = "__all__"


class EducationSerializer(ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'year', 'text']

class PsychologistsSurveySerializer(ModelSerializer):
    psycho_topics = ListField(child=CharField(), required=False, write_only=True)
    education_psychologist_write = ListField(child=EducationSerializer(), required=False, write_only=True)
    rating = DecimalField(read_only=True, max_digits=2, decimal_places=1)
    phone_number = CharField(max_length=45, write_only=True)
    psycho_topic = PsychoTopicSerializer(many=True, read_only=True)
    education_psychologist = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = PsychologistSurvey
        exclude = ['is_approved', 'user']

    def create(self, validated_data):

        psycho_topics_data = validated_data.pop('psycho_topics', [])
        if isinstance(psycho_topics_data, str):
            final_topics = [name.strip() for name in psycho_topics_data.split(",") if name.strip()]
        elif isinstance(psycho_topics_data, list):
            final_topics = []
            for item in psycho_topics_data:
                if isinstance(item, str) and ',' in item:
                    final_topics.extend([name.strip() for name in item.split(",") if name.strip()])
                elif isinstance(item, str):
                    final_topics.append(item.strip())
                else:
                    final_topics.append(item)
        else:
            final_topics = []

        psycho_topics = [PsychoTopic.objects.get_or_create(name=name)[0] for name in final_topics]

        education_json = validated_data.pop('education_psychologist_write', '[]')
        phone_number = validated_data.pop('phone_number')
        education_instances = [Education.objects.create(**edu) for edu in education_json]


        user = CustomUser.objects.get_or_create(phone_number=phone_number, user_type='psychologist')[0]

        survey = PsychologistSurvey.objects.create(user=user, **validated_data)
        survey.psycho_topic.set(psycho_topics)
        survey.education_psychologist.set(education_instances)

        return survey

    def update(self, instance, validated_data):
        # Обновление тем психологии, если они переданы
        psycho_topics_data = validated_data.pop('psycho_topics', None)
        if psycho_topics_data is not None:
            if isinstance(psycho_topics_data, str):
                final_topics = [name.strip() for name in psycho_topics_data.split(",") if name.strip()]
            elif isinstance(psycho_topics_data, list):
                final_topics = []
                for item in psycho_topics_data:
                    if isinstance(item, str) and ',' in item:
                        final_topics.extend([name.strip() for name in item.split(",") if name.strip()])
                    elif isinstance(item, str):
                        final_topics.append(item.strip())
                    else:
                        final_topics.append(item)
            else:
                final_topics = []

            psycho_topics = [PsychoTopic.objects.get_or_create(name=name)[0] for name in final_topics]
            instance.psycho_topic.set(psycho_topics)

        # Обновление образования психолога, если оно передано
        education_data = validated_data.pop('education_psychologist_write', None)
        if education_data is not None:
            instance.education_psychologist.all().delete()  # Удаляем старые записи
            education_instances = [Education.objects.create(**edu) for edu in education_data]
            instance.education_psychologist.set(education_instances)

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

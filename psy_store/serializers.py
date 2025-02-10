import json

from jsonschema.exceptions import ValidationError
from rest_framework.fields import DecimalField, ListField, CharField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from cabinet.models import PsychologistSurvey, Education
from psy_store.models import GiftSession
from wellness.models import PsychoTopic


class GiftSessionSerializer(ModelSerializer):
    class Meta:
        model = GiftSession
        fields = "__all__"


class EducationSerializer(ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'year', 'text']

class PsychologistsSurveySerializer(ModelSerializer):
    # Принимаем psycho_topic как список строк
    psycho_topic = ListField(child=CharField(), required=False)
    # Для образования передаем JSON-строку
    education_psychologist = CharField(write_only=True, required=False)
    rating = DecimalField(read_only=True, max_digits=2, decimal_places=1)

    class Meta:
        model = PsychologistSurvey
        exclude = ['is_approved', 'user']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        # Извлекаем данные для направлений (psycho_topic)
        psycho_topics_data = validated_data.pop('psycho_topic', [])
        # Если данные пришли не в виде списка, например, как строка, обрабатываем
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

        # Создаем или находим объекты PsychoTopic для каждого отдельного названия
        psycho_topics = [PsychoTopic.objects.get_or_create(name=name)[0] for name in final_topics]

        # Обрабатываем образование, которое всегда создается
        education_json = validated_data.pop('education_psychologist', '[]')
        try:
            education_data = json.loads(education_json)
        except json.JSONDecodeError:
            education_data = []
        education_instances = [Education.objects.create(**edu) for edu in education_data]

        # Создаем анкету психолога (без ManyToMany полей)
        survey = PsychologistSurvey.objects.create(user=user, **validated_data)
        # Устанавливаем связи ManyToMany
        survey.psycho_topic.set(psycho_topics)
        survey.education_psychologist.set(education_instances)

        raise ValidationError('fine')
        return survey
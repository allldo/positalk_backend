from rest_framework.fields import DecimalField
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
    psycho_topic = StringRelatedField(many=True)
    education_psychologist = EducationSerializer(many=True)
    rating = DecimalField(read_only=True, max_digits=2, decimal_places=1)

    class Meta:
        model = PsychologistSurvey
        exclude = ['is_approved', 'user']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        psycho_topics_data = self.initial_data.get('psycho_topic', [])
        education_data = self.initial_data.get('education_psychologist', [])

        survey = PsychologistSurvey.objects.create(user=user, **validated_data)

        psycho_topics = []
        for topic_name in psycho_topics_data:
            topic, _ = PsychoTopic.objects.get_or_create(name=topic_name)
            psycho_topics.append(topic)
        survey.psycho_topic.set(psycho_topics)

        education_instances = [Education.objects.create(**edu) for edu in education_data]
        survey.education_psychologist.set(education_instances)

        return survey
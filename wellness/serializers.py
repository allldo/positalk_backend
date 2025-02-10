from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, ListField, SlugField, SerializerMethodField, CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, Serializer

from wellness.models import Article, Question, Answer, Block, Test


class BlockNestedSerializer(ModelSerializer):

    class Meta:
        model = Block
        fields = "__all__"

class ArticleNestedSerializer(ModelSerializer):

    class Meta:
        model = Article
        exclude = ["author", "date_created", "release_datetime", "related_articles", "full_image", "body"]


class ArticleSerializer(ModelSerializer):
    body = BlockNestedSerializer(many=True)
    related_articles = ArticleNestedSerializer(many=True)

    class Meta:
        model = Article
        fields = "__all__"


class AnswerNestedSerializer(ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id', 'title', 'points']

class AnswerNestedDefaultSerializer(Serializer):
    id = IntegerField()
    title = CharField()
    points = IntegerField()

class QuestionNestedSerializer(ModelSerializer):

    answers = AnswerNestedSerializer(many=True)
    class Meta:
        model = Question
        fields = "__all__"


class TestListSerializer(ModelSerializer):

    class Meta:
        model = Test
        exclude = ['questions', 'full_image']


class TestSerializer(ModelSerializer):
    questions = QuestionNestedSerializer(many=True)
    class Meta:
        model = Test
        fields = "__all__"


class TestSubmissionSerializer(Serializer):
    test_slug = SlugField()
    answers = ListField(
        child=IntegerField(),
        help_text="Список ID выбранных ответов", allow_null=True, allow_empty=True, required=False
    )
    answers_colors = ListField(
        allow_null=True,
        allow_empty=True,
        child=ListField(
            child=AnswerNestedDefaultSerializer(),
            help_text="Список ID выбранных ответов для группы"
        ),
        help_text="Список групп ответов, где каждая группа — это список ID выбранных ответов"
    )

class ResultSerializer(ModelSerializer):
    image = SerializerMethodField()
    test_name = SerializerMethodField()
    class Meta:
        model = Test
        fields = ["description", 'image', 'test_name']

    def get_image(self, obj):
        try:
            return f"{settings.CURRENT_DOMAIN}{obj.cover.url}"
        except ValueError:
            return None

    def get_test_name(self, obj):
        return obj.test.title



class CreateQuestionSerializer(Serializer):
    question = CharField()
    scale = CharField()


class QuestionSerializer(ModelSerializer):
    # Можно выводить привязанные ответы как список ID
    answers = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'scale', 'answers']

class AbuseSerializer(Serializer):
    test = PrimaryKeyRelatedField(many=False, queryset=Test.objects.all())
    questions = ListField(child=CreateQuestionSerializer())
    attach_answers = ListField(child=IntegerField())

    def validate_attach_answers(self, value):
        existing_ids = set(Answer.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing_ids
        if missing:
            raise ValidationError(f"Answers with IDs {missing} not found.")
        return value

    def create(self, validated_data):
        questions_data = validated_data['questions']
        answer_ids = validated_data['attach_answers']
        # Получаем объекты Answer по переданным ID
        answers = list(Answer.objects.filter(id__in=answer_ids))
        created_questions = []
        for q_data in questions_data:
            question_text = q_data['question']
            scale = q_data['scale']
            # Создаем новый вопрос (в данном случае поле title используется для текста вопроса)
            question_obj = Question.objects.create(title=question_text, scale=scale)
            # Привязываем ко вновь созданному вопросу все выбранные ответы
            question_obj.answers.set(answers)
            created_questions.append(question_obj)
        zxc =validated_data['test']
        zxc.questions.set(created_questions)
        raise ValidationError({'status': 'Все норм, делаем дальше'})
        return True

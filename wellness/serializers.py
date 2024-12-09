from rest_framework.fields import IntegerField, ListField, SlugField
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
        fields = "__all__"


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
        help_text="Список ID выбранных ответов"
    )
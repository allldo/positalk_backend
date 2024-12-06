from rest_framework.serializers import ModelSerializer

from wellness.models import Article, Question, Answer, Block


class BlockNestedSerializer(ModelSerializer):

    class Meta:
        model = Block
        fields = "__all__"

class ArticleNestedSerializer(ModelSerializer):

    class Meta:
        model = Article
        exclude = ["release_datetime", "related_articles", "full_image", "body"]


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


class TestSerializer(ModelSerializer):
    questions = QuestionNestedSerializer(many=True)
    class Meta:
        model = Article
        fields = "__all__"
from rest_framework.serializers import ModelSerializer

from wellness.models import Article, Question, Answer


class ArticleSerializer(ModelSerializer):

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
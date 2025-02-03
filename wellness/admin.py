from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm, ModelMultipleChoiceField

from wellness.models import Article, Question, Answer, Test, Block, Result, PreferablePrice, CoupleTherapy, Feeling, \
    Relation, WorkStudy, LifeEvent, PsychoTopic

# admin.site.register(Test)
admin.site.register(Result)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

class  QuestionInline(admin.StackedInline):
    model = Question.answers.through
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    def has_module_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

class ArticleInline(admin.StackedInline):
    model = Article.body.through
    extra = 1

class ArticleAdminForm(ModelForm):

    class Meta:
        model = Article
        exclude = ['body']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.instance and self.instance.pk:
    #         self.fields['body'].queryset = Block.objects.filter(
    #             Q(articles=self.instance) | Q(articles=None)
    #         ).distinct()
    #     else:
    #         self.fields['body'].queryset = Block.objects.filter(articles=None)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    inlines = [ArticleInline]
admin.site.register(Article, ArticleAdmin)


# class TestAdminForm(ModelForm):
#     class Meta:
#         model = Test
#         fields = "__all__"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.pk:
#             self.fields['questions'].queryset = Question.objects.filter(
#                 Q(tests=self.instance) | ~Q(tests__isnull=False)
#             ).distinct()
#         else:
#             self.fields['questions'].queryset = Question.objects.filter(tests__isnull=True)

class TestInline(admin.StackedInline):
    model = Test.questions.through
    extra = 1

class ResultInline(admin.StackedInline):
    model = Result
    extra = 1
    fields = ('description', 'cover', 'min_points', 'max_points', 'position')

class TestAdmin(admin.ModelAdmin):
    # form = TestAdminForm
    inlines = [TestInline, ResultInline]
    exclude = ['questions']

admin.site.register(Test, TestAdmin)

admin.site.register(Feeling)
admin.site.register(Relation)
admin.site.register(WorkStudy)
admin.site.register(LifeEvent)
admin.site.register(CoupleTherapy)
admin.site.register(PreferablePrice)
admin.site.register(PsychoTopic)
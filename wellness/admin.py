from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm, ModelMultipleChoiceField

from wellness.models import Article, Question, Answer, Test, Block, Result

admin.site.register(Test)
admin.site.register(Result)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

class ArticleAdminForm(ModelForm):
    class Meta:
        model = Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Показываем только связанные с текущей статьей или свободные блоки
            self.fields['body'].queryset = Block.objects.filter(
                Q(articles=self.instance) | Q(articles=None)
            ).distinct()
        else:
            # Если статья новая, показываем только свободные блоки
            self.fields['body'].queryset = Block.objects.filter(articles=None)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
admin.site.register(Article, ArticleAdmin)
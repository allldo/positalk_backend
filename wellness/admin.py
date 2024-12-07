from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField

from wellness.models import Article, Question, Answer, Test, Block, Result

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Article)
admin.site.register(Result)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
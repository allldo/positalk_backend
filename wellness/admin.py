from django.contrib import admin

from wellness.models import Article, Question, Answer, Test

admin.site.register(Article)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
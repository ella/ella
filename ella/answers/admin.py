from django.contrib import admin
from ella.answers.models import Question, Answer

class AnswerOptions(admin.ModelAdmin):
    ordernig = ('created','text',)
    list_display = ('text','created',)
    list_filter = ('created', 'nick', 'question__text',)
    #inlines = (TaggingInlineOptionsSimple,)
    search_fields = ('name',)

admin.site.register(Question)
admin.site.register(Answer, AnswerOptions)

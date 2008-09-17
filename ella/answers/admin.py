from django.contrib import admin
from ella.answers.models import Question, Answer

class AnswerOptions(admin.ModelAdmin):
    ordernig = ('created','text',)
    list_display = ('text','created',)
    list_filter = ('created', 'nick', 'question__text',)
    search_fields = ('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionOptions(admin.ModelAdmin):
    inlines = (AnswerInline,)

admin.site.register(Question, QuestionOptions)
#admin.site.register(Answer, AnswerOptions)

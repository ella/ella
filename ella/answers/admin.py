from django.contrib import admin
from ella.answers.models import Question, Answer, QuestionGroup
from ella.ellaadmin.options import EllaAdminOptionsMixin, RefererAdminMixin

class AnswerOptions(RefererAdminMixin, admin.ModelAdmin):
    ordernig = ('created','text',)
    list_display = ('text','created',)
    list_filter = ('created', 'nick',)
    search_fields = ('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionOptions(admin.ModelAdmin):
    inlines = (AnswerInline,)

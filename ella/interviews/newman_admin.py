from django.utils.translation import ugettext_lazy as _

from ella import newman

from ella.core.newman_admin import PublishableAdmin
from ella.interviews.models import Interview, Question, Interviewee, Answer

class AnswerInlineAdmin(newman.NewmanTabularInline):
    model = Answer
    extra = 1
    rich_text_fields = {'small': ('content',)}

class QuestionInlineAdmin(newman.NewmanTabularInline):
    raw_id_fields = ('user',)
    model = Question
    extra = 0

class QuestionAdmin(newman.NewmanModelAdmin):
    list_display = ('interview', 'author', 'submit_date', 'answered',)
    list_filter = ('submit_date', 'interview',)
    search_fields = ('content', 'nickname', 'email',)
    inlines = [AnswerInlineAdmin]

class IntervieweeAdmin(newman.NewmanModelAdmin):
    list_display = ('__str__', 'user', 'author',)
    search_fields = ('user__first_name', 'user__last_name', 'name', 'description', 'slug', 'author__name',)
    prepopulated_fields = {'slug' : ('name',)}

class InterviewAdmin(PublishableAdmin):

    suggest_fields = PublishableAdmin.suggest_fields
    suggest_fields.update({'interviewees': ('name', 'slug',)})
    rich_text_fields = {'small': ('description',), None: ('content',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title', 'upper_title', 'slug',)}),
        (_("Content"), {'fields': ('description', 'content',)}),
        (_("Metadata"), {'fields': ('photo', 'interviewees', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': ('reply_from', 'reply_to', 'ask_from', 'ask_to',)}),
    )


newman.site.register(Interviewee, IntervieweeAdmin)
newman.site.register(Interview, InterviewAdmin)
newman.site.register(Question, QuestionAdmin)


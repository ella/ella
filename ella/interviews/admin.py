from django.contrib import admin

from ella.interviews.models import Interview, Question, Interviewee, Answer
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin, EllaAdminInline

class AnswerInlineOptions(EllaAdminInline, admin.TabularInline):
    model = Answer
    extra = 1
    rich_text_fields = {'small': ('content',)}

class QuestionInlineOptions(EllaAdminOptionsMixin, admin.TabularInline):
    raw_id_fields = ('user',)
    model = Question
    extra = 0

class QuestionOptions(admin.ModelAdmin):
    list_display = ('interview', 'author', 'submit_date', 'answered',)
    list_filter = ('submit_date', 'interview',)
    search_fields = ('content', 'nickname', 'email',)
    inlines = (AnswerInlineOptions,)

class IntervieweeOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('__str__', 'user', 'author',)
    search_fields = ('user__first_name', 'user__last_name', 'name', 'description', 'slug', 'author__name',)
    prepopulated_fields = {'slug' : ('name',)}

class InterviewOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('title', 'category', 'ask_from', 'reply_from', 'pk',)
    list_filter = ('ask_from', 'reply_from', 'category', 'authors',)
    date_hierarchy = 'ask_from'
    raw_id_fields = ('photo', 'interviewees',)
    search_fields = ('title', 'description',) # FIXME: 'tags__tag__name',)
    prepopulated_fields = {'slug' : ('title',)}
    inlines = [ QuestionInlineOptions ]
    rich_text_fields = {None: ('description', 'content',)}
#    suggest_fields = {'category': ('tree_path', 'title', 'slug',), 'authors': ('name', 'slug',),
#        'source': ('name',), 'interviewees': ('name', 'author__name', 'user__first_name', 'user__last_name'),}
    suggest_fields = {'authors': ('name', 'slug',), 'source': ('name',),}


admin.site.register(Interviewee, IntervieweeOptions)
admin.site.register(Interview, InterviewOptions)
admin.site.register(Question, QuestionOptions)


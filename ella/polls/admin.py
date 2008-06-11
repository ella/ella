from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.newforms.models import BaseInlineFormset
from django.shortcuts import render_to_response

from ella.tagging.admin import TaggingInlineOptions

from ella.core.admin import PlacementInlineOptions
from ella.ellaadmin import widgets
from ella.core.cache import get_cached_object_or_404
from ella.polls.models import Poll, Contest, Contestant, Quiz, Result, Choice, Vote, Question


def formfield_for_dbfield(fields):
    def _formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in fields:
            kwargs['widget'] = widgets.RichTextAreaWidget(height='small')
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)
    return _formfield_for_dbfield

class ResultFormset(BaseInlineFormset):

    def clean(self):
        if not self.cleaned_data:
            return self.cleaned_data

        validation_error = None
        for d in self.cleaned_data:
            if d['points_from'] > d['points_to']:
                validation_error = ValidationError(ugettext(
                        'Invalid score interval %(points_from)s - %(points_to)s.'
                        'Points dimension from can not be greater than point dimension to.') % d
)
                self.forms[i]._errors = {'points_to': validation_error.messages}
        if validation_error:
            raise ValidationError, ugettext('Invalid score intervals')

        intervals = [ (form_data['points_from'], form_data['points_to']) for form_data in self.cleaned_data ]
        intervals.sort()
        for i in xrange(len(intervals) - 1):
            if intervals[i][1] + 1 > intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is covered by two answers.') % (intervals[i][1])
            elif intervals[i][1] + 1 < intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is not covered by any answer.') % (intervals[i][1] + 1)
        return self.cleaned_data

class ResultTabularOptions(admin.TabularInline):
    model = Result
    extra = 5
    formset = ResultFormset

class ChoiceTabularOptions(admin.TabularInline):
    model = Choice
    extra = 5

class QuestionOptions(admin.ModelAdmin):
    """
    Admin options for Question model:
        * edit inline choices
    """
    inlines = (ChoiceTabularOptions,)
    ordering = ('question',)
    search_fields = ('question',)

    formfield_for_dbfield = formfield_for_dbfield(['question'])

class ChoiceOptions(admin.ModelAdmin):
    """
    Admin options for Choices
    """
    ordering = ('question', 'choice')
    list_display = ('question', 'choice', 'votes', 'points')
    search_fields = ('choice',)

class VoteOptions(admin.ModelAdmin):
    """
    Admin options for votes
    """
    ordering = ('time',)
    list_display = ('time', 'poll', 'user', 'ip_address')

class ContestantOptions(admin.ModelAdmin):
    """
    Admin options for Contestant
    """
    ordering = ('datetime',)
    list_display = ('name', 'surname', 'user', 'datetime', 'contest', 'points', 'winner')

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

class QuestionInlineOptions(admin.options.InlineModelAdmin):
    model = Question
    inlines = (ChoiceTabularOptions,)
    template = 'admin/polls/question/edit_inline/tabular.html'
    extra=10

    formfield_for_dbfield = formfield_for_dbfield(['question'])

class ContestOptions(admin.ModelAdmin):

    def __call__(self, request, url):
        if url and url.endswith('correct_answers'):
            pk = url.split('/')[-2]
            contest = get_cached_object_or_404(Contest, pk=pk)
            contestants = contest.get_correct_answers()
            title = u"%s '%s': %s" % (Contest._meta.verbose_name, contest.title, _('Correct Answers'))
            module_name = Contestant._meta.module_name
            return render_to_response('admin/polls/answer/correct.html',
                {'contestants' : contestants, 'title' : title, 'module_name' : module_name})
        return super(ContestOptions, self).__call__(request, url)

    list_display = ('title', 'category', 'active_from', 'correct_answers', 'get_all_answers_count', 'get_hits', 'full_url',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
    inlines = (QuestionInlineOptions, PlacementInlineOptions, TaggingInlineOptions,)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

class QuizOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'active_from', 'get_hits', 'full_url',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
    inlines = (QuestionInlineOptions, ResultTabularOptions, PlacementInlineOptions, TaggingInlineOptions,)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

class PollOptions(admin.ModelAdmin):
    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])
    list_display = ('title', 'question', 'get_total_votes',)
    list_filter = ('active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results', 'question__question',)
    raw_id_fields = ('question',)


admin.site.register(Poll, PollOptions)
admin.site.register(Contest, ContestOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(Question, QuestionOptions)
admin.site.register(Choice, ChoiceOptions)
admin.site.register(Vote, VoteOptions)
admin.site.register(Contestant, ContestantOptions)


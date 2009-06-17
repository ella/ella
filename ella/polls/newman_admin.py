from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms.models import BaseInlineFormSet
from django.shortcuts import render_to_response
from django.conf import settings
from django.forms.util import ValidationError
from django.template.defaultfilters import striptags
from django.forms import models as modelforms

from ella import newman
from ella.newman import fields

from ella.core.newman_admin import PlacementInlineAdmin, PublishableAdmin
from ella.core.cache import get_cached_object_or_404
from ella.polls.models import Contest, Contestant, Quiz, Result, Choice, Vote, Question, Survey


class ResultFormset(BaseInlineFormSet):
    def clean(self):
        if not self.is_valid():
            return

        validation_error = None
        for i,d in ((i,d) for i,d in enumerate(self.cleaned_data) if d):
            if d['points_from'] > d['points_to']:
                validation_error = ValidationError(ugettext(
                        'Invalid score interval %(points_from)s - %(points_to)s.'
                        'Points dimension from can not be greater than point dimension to.') % d
)
                self.forms[i]._errors = {'points_to': validation_error.messages}
        if validation_error:
            raise ValidationError, ugettext('Invalid score intervals')

        intervals = [ (form_data['points_from'], form_data['points_to']) for form_data in self.cleaned_data if form_data ]
        intervals.sort()
        for i in xrange(len(intervals) - 1):
            if intervals[i][1] + 1 > intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is covered by two answers.') % (intervals[i][1])
            elif intervals[i][1] + 1 < intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is not covered by any answer.') % (intervals[i][1] + 1)
        return self.cleaned_data

class ResultTabularAdmin(newman.NewmanTabularInline):
    model = Result
    extra = 1
    formset = ResultFormset

class ChoiceTabularAdmin(newman.NewmanTabularInline):
    model = Choice
    extra = 1

class QuestionAdmin(newman.NewmanModelAdmin):
    """
    Admin options for Question model:
        * edit inline choices
    """
    list_display = ('__unicode__', 'quiz', 'contest',)
    inlines = (ChoiceTabularAdmin,)
    ordering = ('question',)
    search_fields = ('question',)

    rich_text_fields = {None: ('question',)}


class ChoiceAdmin(newman.NewmanModelAdmin):
    """
    Admin options for Choices
    """
    ordering = ('question', 'choice')
    list_display = ('question', 'choice', 'votes', 'points')
    search_fields = ('choice',)

class VoteAdmin(newman.NewmanModelAdmin):
    """
    Admin options for votes
    """
    ordering = ('time',)
    list_display = ('time', 'poll', 'user', 'ip_address')

class ContestantAdmin(newman.NewmanModelAdmin):
    """
    Admin options for Contestant
    """
    ordering = ('datetime',)
    list_display = ('name', 'surname', 'user', 'datetime', 'contest', 'points', 'winner')
    rich_text_fields = {'small': ('text_announcement', 'text', 'text_results',)}

class QuestionForm(modelforms.ModelForm):
    # create the field here to pass validation
    choices =  fields.ChoiceCustomField(label=_('Choices'))

    class Meta:
        model = Question

    def __init__(self, *args, **kwargs):
        initial = []
        if 'initial' in kwargs:
            pass
        elif 'instance' in kwargs:
            inst = kwargs['instance']
            for choice in Choice.objects.filter(question=inst):
                initial.append(choice)

        self.base_fields['choices'] = fields.ChoiceCustomField(label=_('Choices'), initial=initial)
        super(QuestionForm, self).__init__(*args, **kwargs)

    def get_part_id(self, suffix):
        id_part = self.data.get('choices_widget')
        if not suffix:
            return id_part
        return '%s-%s' % (id_part, suffix)

    def clean(self):
        import pdb;pdb.set_trace()
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance or not self.cleaned_data['choices']:
            return self.cleaned_data
        try:
            choice_ids = map(lambda v: int(v), self.data.getlist('question_set-0-choices-id'))
            choice_points = map(lambda v: int(v), self.data.getlist('question_set-0-choices-points'))
        except:
            raise ValidationError(_(u'Enter a whole number.'))
        choice_texts = self.data.getlist('question_set-0-choices') # choices text
        super(QuestionForm, self).clean()

    def save(self, commit=True):
        import pdb;pdb.set_trace()
        try:
            choice_ids = map(lambda v: int(v), self.data.getlist('question_set-0-choices-id'))
            choice_points = map(lambda v: int(v), self.data.getlist('question_set-0-choices-points'))
        except:
            raise ValidationError(_(u'Enter a whole number.'))
        choice_texts = self.data.getlist('question_set-0-choices') # choices text
        for chid, text, points in zip(choice_ids, choice_texts, choice_points):
            if chid <= 0:
                new_ch = Choice(points=points, choice=text, votes=0, question=self.cleaned_data)
                continue
            ch = Choice.objects.get(pk=chid)
            if ch.choice != text or ch.points != points:
                ch.choice = text
                ch.points = points
                ch.save()

class QuestionInlineAdmin(newman.NewmanTabularInline):
    model = Question
    form = QuestionForm
    #inlines = [ChoiceTabularAdmin]
#    template = 'admin/polls/question/edit_inline/tabular.html'
    #template = 'newman/edit_inline/poll_question.html'
    extra = 1
    #rich_text_fields = {'small': ('question',)}
    fieldsets = ((None, {'fields' : ('question', 'allow_multiple', 'allow_no_choice', 'choices',)}),)

class ContestAdmin(PublishableAdmin):
    def __call__(self, request, url):
        if url and url.endswith('correct_answers'):
            pk = url.split('/')[-2]
            contest = get_cached_object_or_404(Contest, pk=pk)
            contestants = contest.get_correct_answers()
            title = u"%s '%s': %s" % (Contest._meta.verbose_name, contest.title, _('Correct Answers'))
            module_name = Contestant._meta.module_name
            return render_to_response('admin/polls/answer/correct.html',
                {'contestants' : contestants, 'title' : title, 'module_name' : module_name})
        return super(ContestAdmin, self).__call__(request, url)

    list_display = ('title', 'category', 'active_from', 'correct_answers', 'get_all_answers_count', 'pk',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
    inlines = [ QuestionInlineAdmin, PlacementInlineAdmin ]
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {'small': ('text_announcement', 'text', 'text_results',)}

class QuizAdmin(PublishableAdmin):
    list_display = ('title', 'category', 'active_from')
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
    inlines = [QuestionInlineAdmin, ResultTabularAdmin, PlacementInlineAdmin]
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {'small': ('text_announcement', 'text', 'text_results',)}


class PollAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'question', 'get_total_votes', 'pk',)
    list_filter = ('active_from', 'active_till',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results', 'question__question',)
    rich_text_fields = {'small': ('text_announcement', 'text', 'text_results',)}
    suggest_fields = {'question': ('__unicode__', 'question',)}

    fieldsets = (
        (_('Basic'), {'fields' : ('title', 'question', 'active_from', 'active_till')}),
        (_('Texts'), {'fields' : ('text_announcement', 'text', 'text_results',)}),
    )

class SurveyChoiceInlineAdmin(newman.NewmanTabularInline):
    exclude = ('points', 'votes',)
    model = Choice
    extra = 5
    # FIXME: rich text problem with inlines :(
    rich_text_fields = {'small': ('choice',)}


class SurveyAdmin(newman.NewmanModelAdmin):
    exclude = ('quiz', 'contest', 'allow_no_choice', 'allow_multiple')
    list_display = ('__unicode__', 'get_total_votes',)
    list_filter = ('active_from', 'active_till',)
    search_fields = ('question',)
    rich_text_fields = {'small': ('question',)}

    inlines = [SurveyChoiceInlineAdmin]


#newman.site.register(Poll, PollAdmin)
newman.site.register(Survey, SurveyAdmin)
newman.site.register(Contest, ContestAdmin)
newman.site.register(Quiz, QuizAdmin)
newman.site.register(Question, QuestionAdmin)
newman.site.register(Choice, ChoiceAdmin)
newman.site.register(Vote, VoteAdmin)
newman.site.register(Contestant, ContestantAdmin)


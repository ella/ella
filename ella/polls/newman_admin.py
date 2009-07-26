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

class ResultForm(modelforms.ModelForm):

    class Meta:
        model = Result

    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        self.fields['count'].required = False

    def clean(self):
        self.cleaned_data = super(ResultForm, self).clean()
        if not self.cleaned_data['count']:
            self.cleaned_data['count'] = u'0'
        if not self.is_valid():
            return
        return self.cleaned_data

class ResultTabularAdmin(newman.NewmanTabularInline):
    model = Result
    form = ResultForm
    extra = 1
    formset = ResultFormset

class ChoiceTabularAdmin(newman.NewmanTabularInline):
    model = Choice
    extra = 1
    rich_text_fields = {'small': ('choice',)}

class QuestionAdmin(newman.NewmanModelAdmin):
    """
    Admin options for Question model:
        * edit inline choices
    """
    list_display = ('__unicode__', 'quiz', 'contest',)
    inlines = (ChoiceTabularAdmin,)
    ordering = ('question',)
    search_fields = ('question',)

    rich_text_fields = {'small': ('question',)}


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
    choices =  fields.ChoiceCustomField([], label=_('Choices'), required=False, initial=(Choice(id=0, choice=fields.ChoiceCustomField.default_text, points=0),))

    class Meta:
        model = Question

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        existing_object = False
        new_object = False
        if 'instance' in kwargs and 'data' not in kwargs:
            existing_object = True
        elif 'data' not in kwargs:
            new_object = True

        default_text = fields.ChoiceCustomField.default_text
        initial = (Choice(id=0, choice=default_text, points=0),)
        #self.fields['choices'] = fields.ChoiceCustomField(label=_('Choices'), initial=initial, required=False)
        if existing_object:
            # custom field is added when existing-question-form is generated
            inst = kwargs['instance']
            ex_initial = tuple(Choice.objects.filter(question=inst))
            if not ex_initial:
                ex_initial = initial
            self.fields['choices'] = fields.ChoiceCustomField(label=_('Choices'), initial=ex_initial, required=False)
        elif new_object:
            #self.initial['choices'] = initial
            pass

        self.id_part = None
        self.widget_index = 0

    def get_part_id(self, suffix=None):
        self.id_part = '%s-choices' % self.prefix
        if not suffix:
            return self.id_part
        return '%s-%s' % (self.id_part, suffix)

    def clean(self):
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance:
            return self.cleaned_data
        self.cleaned_data = super(QuestionForm, self).clean()
        if not self.cleaned_data['id'] and not self.cleaned_data['question']:
            return self.cleaned_data
        try:
            self.cleaned_data['choice_ids'] = map(lambda v: int(v), self.data.getlist(self.get_part_id('id')))
            self.cleaned_data['choice_points'] = map(lambda v: int(v), self.data.getlist(self.get_part_id('points')))
        except:
            raise ValidationError(_(u'Enter a whole number.'))
        self.cleaned_data['choice_texts'] = self.data.getlist(self.get_part_id()) # choices text
        """
        for tx in self.cleaned_data['choice_texts']:
            if not tx:
                raise ValidationError(_(u'This field cannot be null.'))
        """
        return self.cleaned_data

    def full_clean(self):
        super(QuestionForm, self).full_clean()

    def _get_changed_data(self):
        out = super(QuestionForm, self)._get_changed_data()
        if 'choices' in out and 'question' not in out:
            if len( self.data.getlist(self.get_part_id()) ) > 0:
                return ['question', 'choices']
        return out
    changed_data = property(_get_changed_data)

    def save(self, commit=True):
        out = super(modelforms.ModelForm, self).save(commit=commit)
        instance = self.cleaned_data['id']

        def save_them():
            choice_ids = self.cleaned_data['choice_ids']
            choice_points = self.cleaned_data['choice_points']
            choice_texts = self.cleaned_data['choice_texts'] # choices text
            irange = range(1, len(choice_texts) + 1)
            for chid, text, points, i in zip(choice_ids, choice_texts, choice_points, irange):
                if chid <= 0:
                    if text == fields.ChoiceCustomField.default_text or not text:
                        continue
                    new_ch = Choice(points=points, choice=text, votes=0, question=instance)
                    new_ch.save()
                    continue
                remove = self.data.get(self.get_part_id('%d-DELETE' % i), 'off')
                ch = Choice.objects.get(pk=chid)
                if remove == 'on':
                    ch.delete()
                elif ch.choice != text or ch.points != points:
                    ch.choice = text
                    ch.points = points
                    ch.save()

        if commit:
            save_them()
        else:
            save_m2m = getattr(self, 'save_m2m', None)
            instance = self.instance
            def save_all():
                if save_m2m:
                    save_m2m()
                save_them()
            self.save_m2m = save_all
        return out

class QuestionInlineAdmin(newman.NewmanTabularInline):
    model = Question
    form = QuestionForm
    template = 'newman/edit_inline/poll_question.html'
    rich_text_fields = {'small': ('question',)}
    fieldsets = ((None, {'fields' : ('question', 'allow_multiple', 'allow_no_choice', 'choices')}),)
    extra = 1

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

# FIXME: correct_answers does not work
    list_display = ('admin_link', 'category', 'active_from', 'correct_answers', 'get_all_answers_count', 'pk',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text',)
    inlines = [PlacementInlineAdmin, QuestionInlineAdmin]
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {'small': ('description',), None: ('text',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title', 'slug',)}),
        (_("Content"), {'fields': ('description', 'text',)}),
        (_("Metadata"), {'fields': ('photo', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': (('active_from', 'active_till',),)}),
    )

class QuizAdmin(PublishableAdmin):
#    list_display = ('admin_link', 'category', 'active_from')
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text',)
    inlines = [QuestionInlineAdmin, ResultTabularAdmin, PlacementInlineAdmin]
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {'small': ('description',), None: ('text',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title', 'slug',)}),
        (_("Content"), {'fields': ('description', 'text',)}),
        (_("Metadata"), {'fields': ('photo', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': (('active_from', 'active_till',),)}),
    )

class PollAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'question', 'get_total_votes', 'pk',)
    list_filter = ('active_from', 'active_till',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results', 'question__question',)
    rich_text_fields = {'small': ('text', )}
    suggest_fields = {'question': ('__unicode__', 'question',)}

    fieldsets = (
        (_('Basic'), {'fields' : ('title', 'question', 'active_from', 'active_till')}),
        (_('Texts'), {'fields' : ('text',)}),
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


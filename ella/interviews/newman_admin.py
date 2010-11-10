from django.utils.translation import ugettext_lazy as _, ugettext

from ella import newman

from ella.core.newman_admin import PublishableAdmin
from ella.interviews.models import Interview, Question, Interviewee, Answer
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ValidationError

class AnswerInlineAdmin(newman.NewmanStackedInline):
    model = Answer
    extra = 1
    suggest_fields = {'interviewee': ('__unicode__', 'slug', 'name')}
    rich_text_fields = {'small': ('content',)}

class QuestionInlineAdmin(newman.NewmanTabularInline):
    raw_id_fields = ('user',)
    model = Question
    extra = 0

class QuestionAdmin(newman.NewmanModelAdmin):
    list_display = ('interview', 'author', 'submit_date', 'answered',)
    list_filter = ('submit_date', 'interview',)
    search_fields = ('content', 'nickname', 'email',)
    suggest_fields = {'interview': ('__unicode__', 'title', 'slug')}
    inlines = [AnswerInlineAdmin]

class IntervieweeAdmin(newman.NewmanModelAdmin):
    list_display = ('__str__', 'user', 'author',)
    search_fields = ('user__first_name', 'user__last_name', 'name', 'description', 'slug', 'author__name',)
    prepopulated_fields = {'slug' : ('name',)}

class InterviewForm(ModelForm):

    def clean(self):
        d = super(InterviewForm, self).clean()
        if not self.is_valid():
            return d
        if d['reply_from'] > d['reply_to']:
            raise ValidationError(_('Reply to must be later than reply from.'))
        if d['ask_from'] > d['ask_to']:
            raise ValidationError(_('Ask to must be later than ask from.'))
        if d['ask_from'] > d['reply_from']:
            raise ValidationError(_('Reply from must be later than ask from.'))
        if d['ask_to'] > d['reply_to']:
            raise ValidationError(_('Reply to must be later than ask to.'))
        return d

    class Meta:
        model = Interview

class InterviewAdmin(PublishableAdmin):
    form = InterviewForm

    list_display = list(PublishableAdmin.list_display[:])
    list_display.insert(-2, 'interview_questions_link')

    suggest_fields = PublishableAdmin.suggest_fields
    suggest_fields.update({'interviewees': ('name', 'slug',)})
    rich_text_fields = {'small': ('description',), None: ('content',)}

    def interview_questions_link(self, obj):
        q_total = obj.get_questions().count()
        q_unanswered = obj.unanswered_questions().count()
        return mark_safe('<a href="%sinterviews/question/?interview__publishable_ptr__exact=%d">%d/%d</a>' % (reverse('newman:index'), obj.pk, q_total, q_unanswered))
    interview_questions_link.short_description = ugettext('Questions')
    interview_questions_link.allow_tags = True

    fieldsets = (
        (_("Heading"), {'fields': ('title', 'upper_title', 'slug',)}),
        (_("Content"), {'fields': ('description', 'content',)}),
        (_("Metadata"), {'fields': ('photo', 'interviewees', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': (('reply_from', 'reply_to',), ('ask_from', 'ask_to',),)}),
    )


newman.site.register(Interviewee, IntervieweeAdmin)
newman.site.register(Interview, InterviewAdmin)
newman.site.register(Question, QuestionAdmin)


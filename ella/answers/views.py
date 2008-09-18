from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.template import RequestContext, loader, Context
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from ella.tagging.fields import SuggestTagField
from django.db import connection
from django import forms
from django.contrib.formtools.preview import FormPreview

from ella.tagging.models import Tag, TaggedItem
from ella.tagging.utils import get_tag, get_queryset_and_model
from ella.core.models import Placement
from ella.db.models import Publishable
from ella.utils.paginator import paginate_qset, get_page_no

from ella.answers.models import Question, Answer

# pagination
HP_PAGE_ITEMS = 2
ANSWER_PAGE_ITEMS = 2

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('created','slug',)

class QuestionPreview(FormPreview):
    @property
    def preview_template(self):
        return 'page/answers/question_preview.html'

    @property
    def form_template(self):
        return 'page/answers/question_preview_form.html'

    def done(self, request, cleaned_data):
        form = QuestionForm(request.POST)
        q = form.save(commit=False)
        q.slug = slugify(q.text)
        q.save()
        return  HttpResponseRedirect(
            reverse(
                'answers_question_detail',
                args=[ q.pk, q.slug ]
)
)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ('created', 'question', 'is_hidden',)

class AnswerPreview(FormPreview):
    def __call__(self, request, *args, **kwargs):
        if 'question_id' in kwargs:
            q = Question.objects.get(pk=int(kwargs['question_id']))
            self.state['question'] = q
        return super(AnswerPreview, self).__call__(request, *args, **kwargs)

    @property
    def preview_template(self):
        return 'page/answers/question_answer_preview.html'

    @property
    def form_template(self):
        return 'page/answers/question_answer_preview_form.html'

    def parse_params(self, *args, **kwargs):
        self.question_id = int(kwargs['question_id'])

    def done(self, request, cleaned_data):
        form = AnswerForm(request.POST)
        q = Question.objects.get(pk=self.question_id)
        a = form.save(commit=False)
        a.question = q
        a.save()
        return  HttpResponseRedirect(
            reverse(
                'answers_question_detail',
                args=[ a.question.pk, a.question.slug ]
)
)

def question_detail(request, question_id=None, question_slug=None):
    if not question_id:
        raise Http404
    try:
        qid = int(question_id)
        q = Question.objects.get(pk=int(qid))
    except Question.DoesNotExist:
        raise Http404('Question with id %d not found.' % qid)
    answers = Answer.objects.filter(question=q, is_hidden=False)
    cx = {
        'question': q,
        'answers': answers,
        'user': request.user,
}
    cx.update(paginate_qset(request, answers, items_per_page=ANSWER_PAGE_ITEMS))
    return render_to_response(
        'page/answers/question.html',
        cx,
        RequestContext(cx)
)

def question_list(request):
    form = QuestionForm()
    all_q = Question.objects.all()
    cx = {
        'form': form,
        'questions': all_q,
        'user': request.user,
}
    cx.update(paginate_qset(request, all_q, items_per_page=HP_PAGE_ITEMS))
    return render_to_response(
        'page/answers/question_list.html',
        cx,
        RequestContext(cx)
)

def question_preview(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.slug = slugify(q.text)
            q.save()
            return  HttpResponseRedirect(
                reverse(
                    'answers_question_detail',
                    args=[ q.pk, q.slug ]
)
)
    else:
        form = QuestionForm()
    cx = {
        'form': form,
}
    return render_to_response(
        'page/answers/question_preview.html',
        cx,
        RequestContext(cx)
)

def question_answer(request, question_id):
    q = Question.objects.get(pk=question_id)
    form = AnswerForm()
    cx = {
        'question': q,
        'form': form,
        'user': request.user,
}
    return render_to_response(
        'page/answers/question_answer.html',
        cx,
        RequestContext(cx)
)

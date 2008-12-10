from django import forms
from django.utils.translation import ugettext_lazy as _

class StatusField(forms.CharField):

    def clean(self, value):
        if value not in (None, ''):
            raise forms.ValidationError(_('This field must be empty!'))

class PostForm(forms.Form):
    content = forms.CharField(required=True, widget=forms.Textarea)
    nickname = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    status = StatusField(required=False, label=_('If you enter anything in this field your post will be treated as spam'))
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput())


class ThreadForm(PostForm):
    title = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)
    nickname = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    status = StatusField(required=False, label=_('If you enter anything in this field your post will be treated as spam'))
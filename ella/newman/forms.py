from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

from ella.core.models import Category
from ella.newman.models import DenormalizedCategoryUserRole, AdminUserDraft

class DraftForm(forms.Form):

    def __init__(self, data=None, **kwargs):
        user = kwargs.pop('user', None)
        ct = kwargs.pop('content_type', None)
        super(DraftForm, self).__init__(data=data, **kwargs)
        self.init_form(user, ct)

    def init_form(self, user, ct):
        drafts = AdminUserDraft.objects.filter(
            ct = ct,
            user = user
        )
        choices = (('', u'-- %s --' % _('Presets')),)
        for d in drafts:
            choices += (d.pk, d.__unicode__(),),
        self.fields['drafts'] = forms.ChoiceField(choices=choices, required=False, label='')

class SiteFilterForm(forms.Form):

    def __init__(self, data=None, user=None, **kwargs):
        super(SiteFilterForm, self).__init__(data=data, **kwargs)
        self.init_form(user)

    def init_form(self, user):
        if user.is_superuser:
            cats = Category.objects.filter(tree_parent__isnull=True)
        else:
            category_ids = DenormalizedCategoryUserRole.objects.root_categories_by_user(user)
            cats = Category.objects.filter(pk__in=category_ids)
        choices = ()
        for c in cats:
            choices += (c.pk, c.__unicode__(),),
        self.fields['sites'] = forms.MultipleChoiceField(choices, widget=CheckboxSelectMultiple, required=False)

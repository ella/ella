from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

class SiteFilterForm(forms.Form):

    def __init__(self, data=None, user=None, **kwargs):
        super(SiteFilterForm, self).__init__(data=data, **kwargs)
        self.init_form(user)

    def init_form(self, user):

        from ella.core.models import Category

        cats = Category.objects.filter(tree_parent__isnull=True)
        if not user.is_superuser:
            roles = user.categoryuserrole_set.all()
            cats = []
            for r in roles:
                cats.extend(r.category.all())

        choices = ()
        for c in cats:
            choices += (c.pk, c.__unicode__(),),
        self.fields['sites'] = forms.MultipleChoiceField(choices, widget=CheckboxSelectMultiple)


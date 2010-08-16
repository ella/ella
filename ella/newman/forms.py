from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.contenttypes.models import ContentType

from ella.core.cache.utils import get_cached_list
from ella.core.models import Category
from ella.newman.models import DenormalizedCategoryUserRole, AdminUserDraft
from ella.newman import widgets

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
            cats = get_cached_list(Category, tree_parent__isnull=True)
        else:
            category_ids = DenormalizedCategoryUserRole.objects.root_categories_by_user(user)
            cats = get_cached_list(Category, pk__in=category_ids)
        choices = ()
        for c in cats:
            choices += (c.pk, c.__unicode__(),),
        self.sites_count = len(choices)
        self.fields['sites'] = forms.MultipleChoiceField(choices, widget=CheckboxSelectMultiple, required=False)

class ErrorReportForm(forms.Form):
    err_subject = forms.CharField(label=_('Subject'))
    err_message = forms.CharField(label=_('Message'), widget=forms.Textarea)

BOX_PHOTO_SIZES = (
    ('velka', _('Big')),
    ('standard', _('Standard')),
    ('mala', _('Small')),
)

BOX_PHOTO_FORMATS = (
    ('ctverec', _('Square')),
    ('obdelnik_sirka', _('Rectangle to width')),
    ('obdelnik_vyska', _('Rectangle to height')),
    ('nudle_sirka', _('Noodle to width')),
    ('nudle_vyska', _('Noodle to height')),
)

BOX_TYPES = (
    ('link', _('Link')),
    ('inline', _('Inline')),
)

class EditorBoxForm(forms.Form):
    box_obj_ct = forms.ModelChoiceField(ContentType.objects.all(), None, cache_choices=True, required=True, widget=widgets.ContentTypeWidget, label='')
    box_obj_id = forms.IntegerField(label='', min_value=0, widget=widgets.ForeignKeyGenericRawIdWidget)
    box_photo_size = forms.ChoiceField(choices=BOX_PHOTO_SIZES, required=False, label=_('Size'), initial='standard')
    box_photo_format = forms.ChoiceField(choices=BOX_PHOTO_FORMATS, required=False, label=_('Format'), initial='obdelnik_sirka')
    box_photo_meta_show_title = forms.BooleanField(required=False, label=_('Title'))
    box_photo_meta_show_authors = forms.BooleanField(required=False, label=_('Author'))
    box_photo_meta_show_source = forms.BooleanField(required=False, label=_('Source'))
    box_photo_meta_show_description = forms.BooleanField(required=False, label=_('Description'))
    box_photo_meta_show_detail = forms.BooleanField(required=False, label=_('Magnifying'))
    box_type = forms.ChoiceField(choices=BOX_TYPES, required=False, label=_('Box type'), initial='link')
    box_obj_params = forms.CharField(label=_('Extra parameters'), max_length=300, required=False, widget=forms.Textarea(attrs={'rows': 3, 'style': 'width:98%'}))


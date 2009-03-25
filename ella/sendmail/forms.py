from datetime import datetime
import time
import logging
from hashlib import md5

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType

from django import forms
from django.utils.translation import ugettext_lazy as _

from ella.core.cache import get_cached_object

INIT_PROPS = {
    'target': '',
    'gonzo': '',
}
log = logging.getLogger('ella.sendmail')


def compute_hash(target='', timestamp=''):
    """
    counts md5 hash of options
    this is simple check, if sent data are the same as expected
    (defined in options)

    """
    timestamp = str(timestamp)
    return md5('-'.join((target, timestamp, settings.SECRET_KEY,))).hexdigest()

class SendMailForm(forms.Form):

    def __init__(self, data=None, init_props=INIT_PROPS, **kwargs):
        super(SendMailForm, self).__init__(data=data, **kwargs)
        self.set_init_props(data, init_props)
        self.init_form(self.init_props)

        if not data:
            self.fill_form_values()


    def set_init_props(self, data=None, init_props=INIT_PROPS):
        """set initial form properties
        form is created from data, if it is bound
        from init_props, if not bound
        from options saved in database, if any
        """
        if data:
            # don't want MultiValueDict here - sorry for this hack - FIXME
            init_props = dict(zip(data.keys(), data.values()))

        # copy defalt settings
        self.init_props = INIT_PROPS.copy()

        # set actual time
        now = int(time.mktime(datetime.now().timetuple()))
        self.init_props['timestamp'] = now

        # update defaults with form init params
        self.init_props.update(init_props)

        target_ct, target_id = None, None
        try:
            target_ct, target_id = self.init_props['target'].split(':')
            target_ct, target_id = int(target_ct), int(target_id)
            target_contenttype = get_cached_object(ContentType, pk=target_ct)
            self.target_object = get_cached_object(target_contenttype, pk=target_id)
        except ValueError, ve:
            log.error('ValueError: %s' % str(ve))
        except models.ObjectDoesNotExist, e:
            log.error('Object does not exist: %s' % str(e))

        # defaults for this instance
        self.init_props['target_ct'] = target_ct
        self.init_props['target_id'] = target_id

        # defaults continue
        #self.init_props['gonzo'] = compute_hash(self.init_props['target'], self.init_props['timestamp'])
        self.init_props['gonzo'] = compute_hash(self.init_props['target'])

    def init_form(self, init_props={}):
        """create form by given init_props"""
        self.add_hidden_inputs()
        self.add_normal_inputs()
#        self.arrange_form_by_opts()

    def add_hidden_inputs(self):
        """new hidden input fields, without initial values"""
        hidden = forms.HiddenInput()
        self.fields['gonzo'] = forms.RegexField(self.init_props['gonzo'], widget=hidden)
        self.fields['target'] = forms.RegexField(r'\d+%s\d+' % ':', max_length=128, widget=hidden)
        self.fields['timestamp'] = forms.IntegerField(widget=hidden)

    def add_normal_inputs(self):
        """any other normal inputs"""
        textarea = forms.Textarea()
        self.fields['sender_mail'] = forms.EmailField(label=_("Sender email:"))
        self.fields['sender_name'] = forms.CharField(max_length=40, required=False, label=_("Sender name:"))
        self.fields['recipient_mail'] = forms.EmailField(label=_("Recipient email:"))
        self.fields['custom_message'] = forms.CharField(max_length=300, required=False, widget=textarea, label=_("Email message:"))


    def fill_form_values(self):
        """fill form initial values - only for nonbound form"""
        # TODO: maybe add decorator for nonbound validation ???
        self.fields['gonzo'].initial = self.init_props['gonzo']
        self.fields['target'].initial = self.init_props['target']
        self.fields['timestamp'].initial = self.init_props['timestamp']


    def clean(self):
        """registered user validation and other cleaning"""
        from django.forms.util import ValidationError

        try:
            # target_ct, target_id validation
            target_ct = self.init_props['target_ct']
            target_id = self.init_props['target_id']
            target_ct = get_cached_object(ContentType, pk=target_ct)
            target_object = get_cached_object(target_ct, pk=target_id)

            self.cleaned_data['target_ct'] = target_ct
            self.cleaned_data['target_id'] = target_id
            self.cleaned_data['target_object'] = target_object
        except models.ObjectDoesNotExist:
            raise ValidationError, _("Target object does not exist.")

        return self.cleaned_data


class SendBuddyForm(SendMailForm):

    def add_normal_inputs(self):
        """any other normal inputs"""
        self.fields['sender_mail'] = forms.EmailField(label=_("Sender email:"))
        self.fields['recipient_mail'] = forms.EmailField(label=_("Recipient email:"))
        self.fields['sender_name'] = forms.CharField(max_length=40, required=False, label=_("Sender name:"))

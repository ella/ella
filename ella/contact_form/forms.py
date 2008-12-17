from django import forms

from ella.contact_form.models import Message

from django.utils.translation import ugettext  as _

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message

MessageForm.base_fields["sender"].label = _("Sender email:")
MessageForm.base_fields["subject"].label = _("Subject:")
MessageForm.base_fields["content"].label = _("Message content:")

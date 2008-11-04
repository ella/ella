from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.http import Http404
from django.conf import settings

from ella.core.custom_urls import dispatcher
from ella.sendmail.views import SendMailFormPreview, new_mail, mail_success, mail_error
from ella.sendmail.forms import SendMailForm

SENDMAIL_AJAX_ONLY = getattr(settings, 'SENDMAIL_AJAX_ONLY', False)

def sendmail_custom_urls(request, bits, context):

    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            if SENDMAIL_AJAX_ONLY and not request.is_ajax():
                raise Http404, 'Sendmail is now configured to accept only AJAX calls'
            mail_preview = SendMailFormPreview(SendMailForm)
            return mail_preview(request, context)
        elif bits[0] == slugify(_('success')):
            return mail_success(request, context)
        elif bits[0] == slugify(_('error')):
            return mail_error(request, context)

    if len(bits) == 0:
        if SENDMAIL_AJAX_ONLY and not request.is_ajax():
            raise Http404, 'Sendmail is now configured to accept only AJAX calls'
        return new_mail(request, context)

    raise Http404

dispatcher.register(slugify(_('send mail')), sendmail_custom_urls)

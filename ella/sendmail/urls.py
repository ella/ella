from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher

def sendmail_custom_urls(request, bits, context):

    from ella.sendmail.views import SendMailFormPreview, new_mail, success
    from ella.sendmail.forms import SendMailForm

    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            mail_preview = SendMailFormPreview(SendMailForm)
            return mail_preview(request, context)
        elif bits[0] == slugify(_('success')):
            return success(request, context)

    if len(bits) == 0:
        return new_mail(request, context)

    from django.http import Http404
    raise Http404

dispatcher.register(slugify(_('send mail')), sendmail_custom_urls)

import logging
from smtplib import SMTP

from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core import mail

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ella.core.cache.utils import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from ella.sendmail.forms import SendMailForm, compute_hash
from ella.sendmail.mailer import create_mail


log = logging.getLogger('ella.sendmail')

class SendMailFormPreview(FormPreview):
    @property
    def preview_template(self):
        return get_templates_from_placement('sendmail/preview.html', self.state['placement'])

    @property
    def form_template(self):
        return get_templates_from_placement('sendmail/form.html', self.state['placement'])

    def parse_params(self, context={}):
        self.state.update(context)


    def done(self, request, cleaned_data):
        sender_mail = cleaned_data['sender_mail']
        recipient_mail = cleaned_data['recipient_mail']
        target = cleaned_data['target_object']

        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'

        try:
            send_it(
                sender_mail=sender_mail,
                recipient_mail=recipient_mail,
                target_object=target,
                custom_message=cleaned_data['custom_message'],
)
        except Exception, e:
            log.error('Error during sending e-mail to a buddy. %s' % str(e))
            return HttpResponseRedirect("%s%s/%s/" % (url, slugify(_('send mail')), slugify(_('error'))))

        return HttpResponseRedirect(url)

def send_it(**kwargs):
    """
    Mandatory arguments::

    sender_mail
    recipient_mail
    target_object
    custom_message
    """
    sender_mail = kwargs['sender_mail']
    recipient_mail = kwargs['recipient_mail']
    target = kwargs['target_object']
    custom_message = kwargs['custom_message']
    site = get_cached_object_or_404(Site, pk=settings.SITE_ID)

    mail_body = render_to_string('page/sendmail/mail-body.html', {
        'custom_message' : custom_message,
        'sender_mail' : sender_mail,
        'target' : target,
        'site' : site})
    mail_subject = render_to_string('page/sendmail/mail-subject.html', {
        'sender_mail' : sender_mail,
        'site' : site})

    eml = create_mail(
        mailfrom=settings.ELLA_SENDMAIL_FROM_MAIL,
        mailto=recipient_mail,
        subject=mail_subject,
        plaintext=mail_body,
        htmltext=mail_body
)
    smtp = SMTP(settings.ELLA_SENDMAIL_SMTP_SERVER)
    smtp.sendmail(settings.ELLA_SENDMAIL_FROM_MAIL, recipient_mail, eml.as_string())
    smtp.quit()
    log.info('e-mail to buddy sent to [%s]' % recipient_mail)


def new_mail(request, context):
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
}
    form = SendMailForm(init_props=init_props)
    context['form'] = form
    templates = get_templates_from_placement('sendmail/form.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))


def sendmail_custom_urls(request, bits, context):
    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            mail_preview = SendMailFormPreview(SendMailForm)
            return mail_preview(request, context)
        elif bits[0] == slugify(_('success')):
            return new_mail(request, context)
        elif bits[0] == slugify(_('error')):
            log.error('Error during sending e-mail to a buddy')
        elif bits[0] == slugify(_('raw')):
            if 'sender_mail' not in request.POST:
                obj = context['object']
                ct = ContentType.objects.get_for_model(obj)
                target = '%d:%d' % (obj.pk, ct.pk)
                return HttpResponse(compute_hash(target))
            params = {
                'sender_mail': request.POST['sender_mail'],
                'recipient_mail': request.POST['recipient_mail'],
                'target_object': request.POST['target'],
                'custom_message': request.POST.get('custom_message', ''),
}
            return send_it(**params)

    if len(bits) == 0:
        return new_mail(request, context)

    raise Http404

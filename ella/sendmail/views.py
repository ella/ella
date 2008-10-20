import logging
from smtplib import SMTP
from xml.dom.minidom import Document

from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.conf import settings

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ella.core.cache.utils import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from ella.sendmail.forms import SendMailForm
from ella.sendmail.models import Mail


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
        sender_name = cleaned_data.get('sender_name', '')
        recipient_mail = cleaned_data['recipient_mail']
        target = cleaned_data['target_object']

        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'

        site = get_cached_object_or_404(Site, pk=settings.SITE_ID)

        mail_body = render_to_string('page/sendmail/mail-body.txt', {
            'custom_message' : cleaned_data['custom_message'],
            'sender_name' : sender_name,
            'sender_mail' : sender_mail,
            'object' : target,
            'site' : site})

        mail_subject = render_to_string('page/sendmail/mail-subject.txt', {
            'sender_name' : sender_name,
            'sender_mail' : sender_mail,
            'object' : target,
            'site' : site})

        try:
            mail.send_mail(
                subject=mail_subject.strip(),
                message=mail_body,
                from_email=sender_mail,
                recipient_list=[recipient_mail])
        except Exception, e:
            log.error('Error during sending e-mail to a buddy. %s' % str(e))
            return HttpResponseRedirect("%s%s/%s/" % (url, slugify(_('send mail')), slugify(_('error'))))

        return HttpResponseRedirect(url)


def new_mail(request, context):
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
}
    form = SendMailForm(init_props=init_props)
    context['form'] = form
    templates = get_templates_from_placement('sendmail/form.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def xml_response(response_code, message):
    """
    Returns::

    <response>
        <code>100</code>
        <message>Alles gute.</message>
    </response>
    """
    doc = Document()
    doc.encoding = 'utf-8'
    res = doc.createElement('response')
    doc.appendChild(res)
    code = doc.createElement('code')
    code.appendChild(doc.createTextNode(str(response_code)))
    msg = doc.createElement('message')
    msg.appendChild(doc.createTextNode(message))
    res.appendChild(code)
    res.appendChild(msg)
    return doc.toxml('utf-8')

def xml_sendmail_view(request, context):
    """ View which returns XML to be used with Flash player etc."""
    RESPONSE_OK = 200
    RESPONSE_ERROR = 500
    mandatory_fields = ('sender_mail', 'sender_name', 'recipient_mail',)
    for fld in mandatory_fields:
        if fld not in request.POST:
            res = xml_response(RESPONSE_ERROR, _('Mail not sent because of mandatory parameters were not passed. Please specify all of them.'))
            return HttpResponse(res, mimetype='text/xml;charset=utf-8') # nothing to respond
    Ct = ContentType.objects.get_for_id(context['content_type'].id)
    params = {
        'sender_name': request.POST['sender_name'],
        'sender_mail': request.POST['sender_mail'],
        'recipient_mail': request.POST['recipient_mail'],
        'target_object': context['object'],
        'custom_message': request.POST.get('custom_message', ''),
}
    try:
        send_it(**params)
        res = xml_response(RESPONSE_OK, _('E-Mail successfully sent.'))
    except Exception, e:
        res = xml_response(RESPONSE_ERROR, _('Error sending mail. ') + str(e))
    return HttpResponse(res, mimetype='text/xml;charset=utf-8')

def sendmail_custom_urls(request, bits, context):
    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            mail_preview = SendMailFormPreview(SendMailForm)
            return mail_preview(request, context)
        elif bits[0] == slugify(_('success')):
            return new_mail(request, context)
        elif bits[0] == slugify(_('error')):
            log.error('Error during sending e-mail to a buddy')
            return render_to_response('page/sendmail/sending-error.html', {}, context_instance=RequestContext(request))
        elif bits[0] == slugify('xml'):
            return xml_sendmail_view(request, context)

    if len(bits) == 0:
        return new_mail(request, context)

    raise Http404

import logging
from xml.dom.minidom import Document

from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview
from django.contrib.sites.models import Site
from django.core import mail
from django.conf import settings

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ella.core.cache.utils import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from ella.sendmail.forms import SendMailForm


log = logging.getLogger('ella.sendmail')

SENDMAIL_AJAX_ONLY = getattr(settings, 'SENDMAIL_AJAX_ONLY', False)

def send_it(custom_message, sender_name, sender_mail, target_object, recipient_mail):

    site = get_cached_object_or_404(Site, pk=settings.SITE_ID)

    mail_body = render_to_string(['page/sendmail/mail-body.html'], {
        'custom_message' : custom_message,
        'sender_name' : sender_name,
        'sender_mail' : sender_mail,
        'object' : target_object,
        'site' : site})
    mail_subject = render_to_string(['page/sendmail/mail-subject.html'], {
        'sender_name' : sender_name,
        'sender_mail' : sender_mail,
        'object' : target_object,
        'site' : site})
    mail.send_mail(
        subject=mail_subject.strip(),
        message=mail_body,
        from_email=sender_mail,
        recipient_list=[recipient_mail])

class SendMailFormPreview(FormPreview):

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(SendMailFormPreview, self).__call__(request, *args, **kwargs)


    @property
    def preview_template(self):
        if self.request.is_ajax():
            tpl = 'sendmail/ajax-preview.html'
        else:
            tpl = 'sendmail/preview.html'
        return get_templates_from_placement(tpl, self.state['placement'])

    @property
    def form_template(self):
        if self.request.is_ajax():
            tpl = 'sendmail/ajax-form.html'
        else:
            tpl = 'sendmail/form.html'
        return get_templates_from_placement(tpl, self.state['placement'])

    def parse_params(self, context={}):
        self.state.update(context)


    def done(self, request, cleaned_data):

        target = cleaned_data['target_object']
        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
            if self.request.is_ajax():
                url += "%s/%s/" % (slugify(_('send mail')), slugify(_('success')))
        else:
            url = '/'

        try:
            send_it (
                custom_message=cleaned_data.get('custom_message',''),
                sender_name=cleaned_data.get('sender_name', ''),
                sender_mail=cleaned_data.get('sender_mail', ''),
                target_object=cleaned_data['target_object'],
                recipient_mail=cleaned_data['recipient_mail'])
        except Exception, e:
            log.error('Error during sending e-mail to a buddy. %s' % str(e))
            return HttpResponseRedirect("%s%s/%s/" % (target.get_absolute_url(), slugify(_('send mail')), slugify(_('error'))))

        return HttpResponseRedirect(url)

mail_preview = SendMailFormPreview(SendMailForm)

def new_mail(request, context):
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
    }
    form = SendMailForm(init_props=init_props)
    context['form'] = form

    if request.is_ajax():
        tpl = 'sendmail/ajax-form.html'
    else:
        tpl = 'sendmail/form.html'

    templates = get_templates_from_placement(tpl, context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def mail_success(request, context):
    if request.is_ajax():
        tpl = 'sendmail/ajax-success.html'
    else:
        tpl = 'sendmail/success.html'

    templates = get_templates_from_placement(tpl, context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def mail_error(request, context):
    "Problem in SMTP server, mail didn't sent"

    if request.is_ajax():
        tpl = 'sendmail/ajax-error.html'
    else:
        tpl = 'sendmail/sending-error.html'

    templates = get_templates_from_placement(tpl, context['placement'])
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

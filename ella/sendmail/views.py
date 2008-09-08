from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview
from django.contrib.sites.models import Site
from django.core import mail

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ella.core.cache.utils import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from forms import SendMailForm


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

        site = get_cached_object_or_404(Site, pk=settings.SITE_ID)

        mail_body = render_to_string('page/sendmail/mail-body.html', {
            'custom_message' : cleaned_data['custom_message'],
            'sender_mail' : sender_mail,
            'target' : target,
            'site' : site})
        mail_subject = render_to_string('page/sendmail/mail-subject.html', {
            'sender_mail' : sender_mail,
            'site' : site})

        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'

        try:
            mail.send_mail(
                subject=mail_subject,
                message=mail_body,
                from_email=sender_mail,
                recipient_list=[recipient_mail])
        except:
            return HttpResponseRedirect("%s%s/%s/" % (url, slugify(_('send mail')), slugify(_('error'))))

        return HttpResponseRedirect("%s%s/%s/" % (url, slugify(_('send mail')), slugify(_('success'))))


def new_mail(request, context):
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
}
    form = SendMailForm(init_props=init_props)
    context['form'] = form
    templates = get_templates_from_placement('sendmail/form.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def success(request, context):
    templates = get_templates_from_placement('sendmail/success.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))


from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ella.core.cache.utils import get_cached_object_or_404

from django.core import mail
from forms import SendMailForm
from django.contrib.sites.models import Site

class SendMailFormPreview(FormPreview):

    @property
    def preview_template(self):
        opts = self.state['object']._meta
        cat = self.state['category']
        return [
                'page/category/%s/content_type/%s.%s/%s/sendmail/preview.html' % (cat.path, opts.app_label, opts.module_name, self.state['object'].slug),
                'page/category/%s/content_type%s.%s/sendmail/preview.html' % (cat.path, opts.app_label, opts.module_name),
                'page/category/%s/sendmail/preview.html' % cat.path,
                'page/content_type/%s.%s/sendmail/preview.html' % (opts.app_label, opts.module_name),
                'page/sendmail/preview.html',
            ]

    @property
    def form_template(self):
        opts = self.state['object']._meta
        cat = self.state['category']
        return [
                'page/category/%s/content_type/%s.%s/%s/sendmail/form.html' % (cat.path, opts.app_label, opts.module_name, self.state['object'].slug),
                'page/category/%s/content_type%s.%s/sendmail/form.html' % (cat.path, opts.app_label, opts.module_name),
                'page/category/%s/sendmail/form.html' % cat.path,
                'page/content_type/%s.%s/sendmail/form.html' % (opts.app_label, opts.module_name),
                'page/sendmail/form.html',
            ]

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

        return HttpResponseRedirect(url)


def new_mail(request, context):

    cat = context['category']
    opts = context['object']._meta
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
}
    form = SendMailForm(init_props=init_props)
    context['form'] = form
    templates = (
        'page/category/%s/content_type/%s.%s/%s/sendmail/form.html' % (cat.path, opts.app_label, opts.module_name, context['object'].slug),
        'page/category/%s/content_type%s.%s/sendmail/form.html' % (cat.path, opts.app_label, opts.module_name),
        'page/category/%s/sendmail/form.html' % cat.path,
        'page/sendmail/form.html',
)
    return render_to_response(templates, context, context_instance=RequestContext(request))


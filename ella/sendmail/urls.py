from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import resolver
from ella.sendmail import views

urlpatterns = patterns('',
    url(r'^$', views.new_mail, name='sendmail-new'),
    url(r'^%s/$' % slugify(_('preview')), views.mail_preview, name='sendmail-preview'),
    url(r'^%s/$' % slugify(_('success')), views.mail_success, name='sendmail-success'),
    url(r'^%s/$' % slugify(_('error')), views.mail_error, name='sendmail-error'),
    url(r'^%s/$' % slugify(_('xml')), views.xml_sendmail_view, name='sendmail-xml'),
)

resolver.register(urlpatterns, prefix=slugify(_('send mail')))

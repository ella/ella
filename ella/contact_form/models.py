import logging
from datetime import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("ella.contact_form")

class Recipient(models.Model):

    email = models.EmailField(_("Email"))
    sites = models.ManyToManyField(Site)

    class Meta:
        verbose_name = _('Contact form recipient')
        verbose_name_plural = _('Contact form recipients')

    def __unicode__(self):
        return self.email

class Message(models.Model):
    sender  = models.EmailField(_("Sender email"), blank=True)
    subject = models.CharField(_("Subject"), max_length=255,blank=True)
    content = models.TextField(_("Message content"))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    class Meta:
        verbose_name = _('Contact form message')
        verbose_name_plural = _('Contact form messages')

    def __unicode__(self):
        return "%s %s: %s" % (self.created, self.sender or _("(anonymous)"), self.subject or _("(no subject)"))

    def send(self, site=settings.SITE_ID):
        """
        Sends emails with contanct form submitted, returns number of email sent
        """
        recipients = Recipient.objects.filter(sites=site)
        if not recipients:
            return 0
        recipients = [r.email for r in recipients]

        # Cast to unicode, because SMTP object can not handle with proxies
        subject = unicode(_("Contact form submitted"))
        content = unicode(_("From: %(sender)s\nSubject: %(subject)s\n\n%(content)s") % {
            'sender':self.sender, 'subject':self.subject, 'content':self.content})
        send_mail(subject, content, settings.ELLA_SENDMAIL_FROM_MAIL, recipients)

        count = len(recipients)
        logger.info('Contact form submitted, %d email(s) sent.' % count)
        return count

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable

class Article(Publishable):
    """
    ``Article`` is the most common publishable object. It can be used for 
    news on internet news pages, blog posts on smaller blogs or even for 
    news on an organization's home page.
    """
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True, db_index=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    content = models.TextField(_('Content'), default='')

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')




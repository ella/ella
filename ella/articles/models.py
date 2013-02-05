from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable


class Article(Publishable):
    """
    ``Article`` is the most common publishable object. It can be used for
    news on internet news pages, blog posts on smaller blogs or even for
    news on an organization's home page.
    """
    content = models.TextField(_('Content'), default='')

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable


class XArticle(Publishable):
    """
    ``XArticle`` is extra publishable descendant for testing.
    Is used for possibility testing descendants of publishable
    with different content type
    """
    content = models.TextField(_('Content'), default='')

    class Meta:
        verbose_name = _('XArticle')
        verbose_name_plural = _('XArticles')

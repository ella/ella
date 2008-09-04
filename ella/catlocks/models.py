from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Category
from ella.core.cache import CachedForeignKey
from ella.catlocks.forms import CategoryLockForm

class CategoryLock(models.Model):
    category = CachedForeignKey(Category, verbose_name=_('Category'), unique=True)
    password = models.CharField(_('Password'), max_length=255)

    class Meta:
        verbose_name = _('Category Lock')
        verbose_name_plural = _('Category Locks')

    def __unicode__(self):
        return u'Locked Category %s' % self.category

    def form(self, *args, **kwargs):
        return CategoryLockForm(*args, **kwargs)


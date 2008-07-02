import logging

from django.db import models, connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

# from ella.menu.models import * # problem with concrete import Menu, MenuItem models
from ella.core.models import Category

log = logging.getLogger('ella.menu')

def highlight_mark(item, obj, stack=[]):
    if item == obj:
        log.debug('Highlighting item %s' % item)
        setattr(item, 'selected_item', True)
        setattr(item, 'mark', True)
    if item in stack:
        log.debug('Highlighting stack item %s' % item)
        setattr(item, 'mark', True)
    return item

class MenuItemManager(models.Manager):

    # TODO @cache_this, pocitat klic zatim podle kategorie (koderi pouzivaji v {% menu%} zatim jen category objekty
    def get_level(self, menu, level, obj):
        log.debug('looking for menu level %s' % level)
        if not obj:
            qs = self.model.objects.filter(menu=menu)
        else:
            ct = ContentType.objects.get_for_model(obj)
            qs = self.model.objects.filter(menu=menu, target_ct=ct, target_id=obj.pk)
        if not qs:
            log.error('Empty QuerySet! Women and children first')
            return None
        stack = [] # [a/b/c/d, a/b/c, a/b, a]
        mi = qs.all()[0]
        while mi:
            stack.append(mi)
            mi = mi.parent
        log.debug('stack: %s' % stack)
        if level == 1:
            qs = self.model.objects.filter(menu=menu, parent__isnull=True)
            # TODO najit potomky a nechat pomoci nich naplnit stack
            out = qs.order_by('order')
            return map(lambda x: highlight_mark(x, obj, stack), out)
        stack_item = 'UNASSIGNED'
        for i in range(level - 1):
            stack_item = stack.pop()
            qs = self.model.objects.filter(menu=menu, parent=stack_item)
        log.debug('Returning menu items for parent=%s' %  stack_item)
        # highlight items, and mark selected item
        out = qs.order_by('order')
        return map(lambda x: highlight_mark(x, obj, stack), out)

import logging

from django.db import models, connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

# from ella.menu.models import * # problem with concrete import Menu, MenuItem models
from ella.core.models import Category
from ella.core.cache.utils import cache_this

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

def get_level_key(func, self, menu, level, obj):
    return 'ella.menu.managers.get_level:%s:%s:%s' % (menu, level, obj)

class MenuItemManager(models.Manager):

    @cache_this(get_level_key)
    def get_level(self, menu, level, obj):
        """
        TODO (cz)::
            Hledame menu urovne ``level``, kde je vybranou polozkou ``obj``.
            Pokud ``obj`` neni odkazovana primo v navolene urovni ``level``,
            snazime se aspon udelat highlight, pokud je to mozne (je-li ``level``
            +-1 uroven od polozky).

        Returns::
            [MenuItem, ..., MenuItem]
        """

        log.debug('looking for menu level %s' % level)
        if not obj:
            qs = self.model.objects.filter(menu=menu)
        else:
            ct = ContentType.objects.get_for_model(obj)
            qs = self.model.objects.filter(menu=menu, target_ct=ct, target_id=obj.pk)
            if not qs and isinstance(obj, Category):
                par = obj.tree_parent
                while par:
                    qs = self.model.objects.filter(menu=menu, target_ct=ct, target_id=par.pk)
                    par = par.tree_parent
                    if qs:
                        break
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
        if len(stack) < (level - 1):
            log.warning('Wrong menu level %d! Stack length %d. Stack: %s' % (level, len(stack), str(stack)))
            return []
        for i in range(level - 1):
            stack_item = stack.pop()
            qs = self.model.objects.filter(menu=menu, parent=stack_item)
        log.debug('Returning menu items for parent=%s' %  stack_item)
        # highlight items, and mark selected item
        out = qs.order_by('order')
        return map(lambda x: highlight_mark(x, obj, stack), out)

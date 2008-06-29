from django.db import models, connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ella.menu.models import *


class MenuItemManager(models.Manager):

    def get_for_menu(self, menu):
        """
        returns menu items asociated with Menu instance.
        Only first level MenuItem instances returned. Nested
        should be accessed via MenuItem.subitems() method.
        """
        qs = self.model.objects.filter(menu=menu, parent__isnull=True)
        return qs.order_by('order')

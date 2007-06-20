from django.db import models

class Apple(models.Model):
    color = models.CharField(maxlength=20)
    def __str__(self):
        return '%s apple' % (self.color,)
    def get_absolute_url(self):
        return '/test/list/apples/%s/' % self.color

class Orange(models.Model):
    cm = models.PositiveIntegerField()
    def __str__(self):
        return '%scm orange' % (self.cm,)


from django import VERSION
from django.contrib import admin

if VERSION[2] == 'newforms-admin':
    admin.site.register([Apple, Orange ])


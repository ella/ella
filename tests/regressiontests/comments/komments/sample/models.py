from django.db import models

class Apple(models.Model):
    color = models.CharField(maxlength=20)
    def __unicode__(self):
        return u'%s apple' % (self.color,)
    def get_absolute_url(self):
        return u'/test/list/apples/%s/' % self.color

class Orange(models.Model):
    cm = models.PositiveIntegerField()
    def __unicode__(self):
        return u'%scm orange' % (self.cm,)


from django.contrib import admin

admin.site.register(Apple)
admin.site.register(Orange)


from django.db import models
from django.utils.translation import ugettext_lazy as _

class Type(models.Model):
    '''
    just some model that will be refferenced by Spam
    '''
    name = models.CharField(max_length=255)
    description = models.TextField()

class Spam(models.Model):
    '''
    sample model from http://south.aeracode.org/wiki/Tutorial
    '''
    weight = models.FloatField()
    expires = models.DateTimeField()
    name = models.CharField(max_length=255)
    count = models.IntegerField(null=True)
    type = models.ForeignKey(Type)

    class Meta:
        unique_together = (('name', 'expires'),)
        verbose_name = _('Spam')
        verbose_name_plural = _('Spam')


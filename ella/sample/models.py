from django.db import models
from django.utils.translation import ugettext_lazy as _

class Type(models.Model):
    '''
    just some model that will be refferenced by Spam
    '''
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def __unicode__(self):
        return self.name

class Spam(models.Model):
    '''
    sample model from http://south.aeracode.org/wiki/Tutorial
    '''
    weight = models.FloatField()
    expires = models.DateTimeField()
    name = models.CharField(max_length=255)
    count = models.IntegerField(null=True, blank=True)
    type = models.IntegerField()

    class Meta:
        unique_together = (('name', 'expires'),)
        verbose_name = _('Spam')
        verbose_name_plural = _('Spam')

    def __unicode__(self):
        return self.name


# custom primary key testing
# http://www.djangoproject.com/documentation/models/custom_pk/

class Employee(models.Model):
    employee_code = models.CharField(max_length=10, primary_key=True, db_column='code')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    class Meta:
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

class Business(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    employees = models.ManyToManyField(Employee)

    class Meta:
        verbose_name_plural = 'businesses'

    def __unicode__(self):
        return self.name


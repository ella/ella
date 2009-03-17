from django.db import models


class Spam(models.Model):
    '''
    sample model from http://south.aeracode.org/wiki/Tutorial
    '''
    weight = models.FloatField()
    expires = models.DateTimeField()
    name = models.CharField(max_length=255)


from django.db import models

class Apple(models.Model):
    color = models.CharField(maxlength=20)
    def __str__(self):
        return '%s apple' % (self.color,)

class Orange(models.Model):
    cm = models.PositiveIntegerField()
    def __str__(self):
        return '%scm orange' % (self.cm,)


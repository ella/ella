from django.db import models

class Apple(models.Model):
    color = models.CharField(maxlength=20)

class Orange(models.Model):
    weight = models.PositiveIntegerField()


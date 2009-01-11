
from django.db import models

class SampleModel(models.Model):
    r = models.DecimalField(decimal_places=2, max_digits=4, db_index=True)

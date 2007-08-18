from django.db import models, transaction


class RelatedManager(models.Manager):
    def get_query_set(self):
        return super(RelatedManager, self).get_query_set().select_related()

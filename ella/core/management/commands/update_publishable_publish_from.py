from datetime import datetime

from django.db.models import Min
from django.core.management.base import NoArgsCommand

from ella.core.models import Publishable

class Command(NoArgsCommand):
    help = 'Update publish_from field on Publishable'

    def handle(self, *test_labels, **options):
        qset = Publishable.objects.annotate(min_publish_from=Min('placement__publish_from'))
        default = datetime(3000, 1, 1)
        for p in qset.iterator():
            d = p.min_publish_from and p.min_publish_from or default
            if p.publish_from != d:
                Publishable.objects.filter(pk=p.pk).update(publish_from=d)


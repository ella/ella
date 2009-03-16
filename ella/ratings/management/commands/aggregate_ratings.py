from django.core.management.base import NoArgsCommand
from django.db import transaction

from ella.utils import installedapps
installedapps.init_logger()

# Logging must be inicialized
from ella.ratings.aggregation import transfer_data

class Command(NoArgsCommand):
    help = 'Aggregate ratings'

    @transaction.commit_on_success
    def handle(self, **options):
        transfer_data()

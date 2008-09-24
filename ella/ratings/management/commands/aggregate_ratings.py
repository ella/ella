from django.core.management.base import NoArgsCommand

from ella.ratings.aggregation import transfer_data

class Command(NoArgsCommand):
    help = 'Aggregate ratings'

    def handle(self, **options):
        transfer_data()
from django.core.management.base import NoArgsCommand

from ella.core.management import generate_publish_signals

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        generate_publish_signals()

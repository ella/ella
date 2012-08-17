from django.core.management.base import NoArgsCommand

from ella.core.management import regenerate_publish_signals


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        regenerate_publish_signals()

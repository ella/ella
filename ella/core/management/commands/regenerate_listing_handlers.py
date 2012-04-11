from django.core.management.base import NoArgsCommand

from ella.core.management import regenerate_listing_handlers

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        regenerate_listing_handlers()

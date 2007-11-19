from django.core.management.base import BaseCommand
from optparse import make_option

class Command(BaseCommand):
    help = 'Fetch all registered imports'
    def handle(self, *test_labels, **options):
        from ella.imports.models import fetch_all
        fetch_all()

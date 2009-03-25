import os
import codecs

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates filesystem templates from database templates.'
    args = "output_template_directory"

    def handle(self, template_dir, **options):
        from django.conf import settings
        from ella.db_templates.models import DbTemplate, InvalidTemplate

        # go directly to templates dir
        os.chdir(template_dir)
        created = 0

        for t in DbTemplate.objects.filter(site__id=settings.SITE_ID):
            t.delete()

        for dir in os.walk('.'):

            dir_name = dir[0]
            for file in dir[2]:
                path = '%s/%s' % (dir_name, file)
                # every path begins with './'
                path = path.replace('./', '')

                try:
                    template = codecs.open(path, "r", "utf-8").read()
                    DbTemplate.objects.create_from_string(template_string=template, name=path)
                    created += 1
                except InvalidTemplate:
                    print path, ':', 'template is invalid'

        return created



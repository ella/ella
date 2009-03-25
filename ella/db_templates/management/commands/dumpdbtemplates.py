import os
import codecs

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates filesystem templates from database templates.'
    args = "output_template_directory"

    def handle(self, template_dir, **options):
        from django.conf import settings
        from ella.db_templates.models import DbTemplate

        # create non existent directory
        if not os.path.isdir(template_dir):
            os.makedirs(template_dir)

        os.chdir(template_dir)
        for i in DbTemplate.objects.filter(site__id=settings.SITE_ID):
            # create all dirs from template name
            path = '/'.join(i.name.split('/')[:-1])
            if not os.path.isdir(path):
                os.makedirs(path)

            # dump unicode template
            f = codecs.open(i.name, "w", "utf-8")
            f.write(i.get_text())
            f.close()



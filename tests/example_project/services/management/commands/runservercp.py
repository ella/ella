from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os

import cherrypy

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True,
            help='Tells Django to NOT use the auto-reloader.'),
        make_option('--adminmedia', dest='admin_media_path', default='',
            help='Specifies the directory from which to serve admin media.'),
    )
    help = "Starts a lightweight Web server for development."
    args = '[optional port number, or ipaddr:port]'

    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        import django
        from django.core.servers.basehttp import AdminMediaHandler
        from django.core.handlers.wsgi import WSGIHandler
        if args:
            raise CommandError('Usage is runservercp %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        use_reloader = options.get('use_reloader', True)
        admin_media_path = options.get('admin_media_path', '')

        from django.conf import settings
        from django.utils import translation
        print "Validating models..."
        self.validate(display_num_errors=True)
        print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
        print "Development server is running at http://%s:%s/" % (addr, port)

        # django.core.management.base forces the locale to en-us. We should
        # set it up correctly for the first request (particularly important
        # in the "--noreload" case).
        translation.activate(settings.LANGUAGE_CODE)

        try:
            path = admin_media_path or django.__path__[0] + '/contrib/admin/media'

            handler = AdminMediaHandler(WSGIHandler(), path)
            cherrypy.config.update({
                    'server.socket_host': addr,
                    'server.socket_port': int(port),
                    'engine.autoreload_on':  use_reloader
                })

            cherrypy.tree.graft(handler, '/')

            cherrypy.engine.start()
            cherrypy.engine.block()
        finally:
            cherrypy.engine.exit()


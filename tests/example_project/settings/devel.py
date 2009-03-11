from os.path import dirname, join, isfile
import logging.config

# init logger
LOGGING_CONFIG_FILE = join(dirname(djangobaseproject.__file__), 'settings', 'logger_devel.ini')
if isinstance(LOGGING_CONFIG_FILE, basestring) and isfile(LOGGING_CONFIG_FILE):
    logging.config.fileConfig(LOGGING_CONFIG_FILE)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
)

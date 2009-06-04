from time import strftime

from django.conf import settings

from ella.newman.utils import set_user_config
from ella.newman.config import USER_CONFIG, CATEGORY_FILTER

class AdminSettingsMiddleware(object):
    """
    Middleware appends to request.user variable his AdminSettings
    due to minimalization of number of database queries.
    """
    def process_request(self, request):
        if not request.session:
            return
        if not USER_CONFIG in request.session:
            return
        user = request.user
        cfg = request.session[USER_CONFIG]
        if CATEGORY_FILTER in cfg:
            root_category_ids = cfg[CATEGORY_FILTER]
            set_user_config(user, CATEGORY_FILTER, root_category_ids)

    def process_response(self, request, response):
        return response

class ErrorOutputMiddleware(object):
    """
    Middleware for debug purposes only. Suitable when digging HTTP 500 responses
    to AJAX/Flash requests. No debilproof, works on unix-like fs only.
    """
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        if not hasattr(settings, 'ERROR_OUTPUT_DIRECTORY'):
            return response
        if response.status_code >= 500 or response.status_code == 404:
            stamp = strftime('%Y%m%d,%H-%M-%S')
            fname = '%s/%s_%d.html' % (settings.ERROR_OUTPUT_DIRECTORY, stamp, response.status_code)
            f = file(fname, 'w')
            f.write(response.content)
            f.close()
        return response

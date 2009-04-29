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
        if not (response.status_code >= 200 and response.status_code < 302):
            f = file('/tmp/last_%d.html' % response.status_code, 'w')
            f.write(response.content)
            f.close()
        return response

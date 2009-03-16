from django.conf import settings
from ella.newman.utils import decode_category_filter_json
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
            root_category_ids = decode_category_filter_json(cfg[CATEGORY_FILTER])
            setattr(user, CATEGORY_FILTER, root_category_ids)

    def process_response(self, request, response):
        return response

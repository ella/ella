from time import strftime

from ella.newman.conf import newman_settings
from ella.newman.utils import set_user_config

class AdminSettingsMiddleware(object):
    """
    Middleware appends to request.user variable his AdminSettings
    due to minimalization of number of database queries.
    """
    def process_request(self, request):
        if not request.session:
            return
        if not newman_settings.USER_CONFIG in request.session:
            return
        user = request.user
        cfg = request.session[newman_settings.USER_CONFIG]
        if newman_settings.CATEGORY_FILTER in cfg:
            root_category_ids = cfg[newman_settings.CATEGORY_FILTER]
            set_user_config(user, newman_settings.CATEGORY_FILTER, root_category_ids)

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
        if not hasattr(newman_settings, 'ERROR_OUTPUT_DIRECTORY'):
            return response
        if response.status_code >= 500 or response.status_code == 404:
            stamp = strftime('%Y%m%d,%H-%M-%S')
            fname = '%s/%s_%d.html' % (newman_settings.ERROR_OUTPUT_DIRECTORY, stamp, response.status_code)
            f = file(fname, 'w')
            f.write(response.content)
            f.close()
        return response

class ProfilerMiddleware(object):
    "Parody to profiler."
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        from ella.newman.utils import PROFILER
        import logging
        log = logging.getLogger('ella.newman')
        if PROFILER.has_data:
            log.info('******** PROFILER SUMMARY:')
            PROFILER.log_summary(log.info)
            PROFILER.reset()
            log.info('******** END')
        return response


class SQLDebugMiddleware(object):

    def format_qstr(self, q):
        q = q.replace('"', '')
        # TODO: some formatting here
        return q


    def process_response(self, request, response):
        if response.status_code != 200 or not response['Content-Type'].startswith('text'):
            return response

        from django.db import connection
        queries = connection.queries
        cnt = len(queries)
        print "SQL ====="
        print "%d queries for %s" % (cnt, request.META['PATH_INFO'])

        for q in connection.queries:
            print "%s\t%s" % (q['time'], self.format_qstr(q['sql']))
        print "===== %d SQL Queries" % cnt

        return response

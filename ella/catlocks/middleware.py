import re
import logging
log = logging.getLogger('ella.catlocks.middleware')

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string

from ella.catlocks.models import CategoryLock
from ella.catlocks.forms import CATEGORY_LOCK_FORM

CATEGORY_LOCK_PASSWD = '__CATEGORY_LOCK_PASSWD__'
CATEGORY_LOCK_ERR_CAT = 'CATEGORY_LOCK_ERR_CAT'

class CategoryLockMiddleware(object):
    def __init__(self):
        fcats = {}
        for cl in CategoryLock.objects.filter(category__site__id=settings.SITE_ID):
            fcats[cl.category.tree_path] = cl
        self.reg = re.compile('^(/' + '/|/'.join(fcats.keys()) + '/)')
        self.forbidden_cats = fcats

    def check_password(self, request, cl):
        if CATEGORY_LOCK_PASSWD in request.session and cl.password in request.session[CATEGORY_LOCK_PASSWD]:
            # everything is authenticated
            return None
        if request.method == 'POST' and CATEGORY_LOCK_FORM in request.POST:
            # logging in
            form = cl.form(request.POST)
            if form.is_valid() and form.cleaned_data['password'] == cl.password:
                # authenticated
                request.session.setdefault(CATEGORY_LOCK_PASSWD, []).append(cl.password)
                request.session.modified = True
                return HttpResponseRedirect(request.path)
        else:
            form = cl.form()

        request.session[CATEGORY_LOCK_ERR_CAT] = cl.category

        url = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(url)

    def process_request(self, request):
        if self.reg.match(request.path):
            for c in self.forbidden_cats.keys():
                if request.path.startswith('/' + c + '/'):
                    return self.check_password(request, self.forbidden_cats[c])
            else:
                log.warning('%s is protected, but no password found.', request.path)
                return HttpResponseForbidden()

    def process_response(self, request, response):
        if request.method != 'POST' and hasattr(request, 'session') and CATEGORY_LOCK_ERR_CAT in request.session:
            del request.session[CATEGORY_LOCK_ERR_CAT]
        return response


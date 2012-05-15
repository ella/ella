import re

from django.shortcuts import redirect

from ella.core.urls import res

LEGACY_RES = map(re.compile,(
    r'^/%(cat)s/%(year)s/%(month)s/%(day)s/%(ct)s/%(slug)s/$' % res,
    r'^/%(year)s/%(month)s/%(day)s/%(ct)s/%(slug)s/$' % res,
    r'^/%(cat)s/%(year)s/%(month)s/%(day)s/%(ct)s/%(slug)s/%(rest)s$' % res,
    r'^/%(year)s/%(month)s/%(day)s/%(ct)s/%(slug)s/%(rest)s$' % res,

    r'^/%(cat)s/%(ct)s/%(id)s-%(slug)s/%(rest)s$' % res,
    r'^/%(ct)s/%(id)s-%(slug)s/%(rest)s$' % res,
    r'^/%(cat)s/%(ct)s/%(id)s-%(slug)s/$' % res,
    r'^/%(ct)s/%(id)s-%(slug)s/$' % res,
))

class LegacyRedirectMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        for r in LEGACY_RES:
            match = r.match(request.path)
            if match:
                d = match.groupdict()
                if 'day' in d:
                    # non-static urls
                    new_path = request.path.replace(
                        '/'.join(d[k] for k in ('year', 'month', 'day', 'content_type')),
                        '/'.join(d[k] for k in ('year', 'month', 'day')),
                    )
                else:
                    # static urls
                    new_path = request.path.replace(
                        '%s/%s-%s' % tuple(d[k] for k in ('content_type', 'id', 'slug')),
                        '%s-%s' % tuple(d[k] for k in ('id', 'slug')),
                    )

                return redirect(new_path, permanent=True)

        return response

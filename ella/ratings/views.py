from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
# gettext_lazy is not needed
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.sites.models import Site

from ella.ratings.models import *
from ella.core.cache import get_cached_object_or_404

current_site = Site.objects.get_cuurent()

CONTENT_TYPE_CT = ContentType.objects.get_for_model(ContentType)
def rate(request, content_type_id, object_id, plusminus=1):
    """
    Add a simple up/down vote for a given object.
    redirect to object's get_absolute_url() on success.

    More granularity can be achieved via setting plusminus to something else than +/-1.

    Params:
        content_type_id: model's content_type
        object_id: id of the target object
        plusminus: rating itself

    Raises:
        Http404 if no content_type or model is associated with the given IDs
    """
    ct = get_cached_object_or_404(CONTENT_TYPE_CT, pk=content_type_id)
    target = get_cached_object_or_404(ct, pk=object_id)

    if 'next' in request.GET and request.GET['next'].startswith('/'):
        url = request.GET['next']
    elif hasattr(target, 'get_absolute_url'):
        url = target.get_absolute_url()
    else:
        url = request.META.get('HTTP_REFERER', '/')
    response = HttpResponseRedirect(url)

    # ANTI-SPAM shortcuts
    if request.user.is_authenticated():
        cook = request.session.get(RATINGS_COOKIE_NAME, [])
        if (ct.id, target.id) in cook:
            request.user.message_set.create(message=_('You have already rated this object.'))
            return response
    else:
        # check anti spam cookie
        cook = request.COOKIES.get(RATINGS_COOKIE_NAME, '').split(',')
        if '%s:%s' % (ct.id, target.id) in cook:
            # fail silently
            return response

    kwa = {'amount' : ANONYMOUS_KARMA}
    if request.user.is_authenticated():
        kwa['user'] = request.user
        profile = request.user.get_profile()
        kwa['amount'] = getattr(profile, 'karma', INITIAL_USER_KARMA)

    kwa['amount'] *= plusminus

    if request.META.has_key('REMOTE_ADDR'):
        kwa['ip_address'] = request.META['REMOTE_ADDR']

    # do the rating
    rt = Rating(target_ct_id=content_type_id, target_id=object_id, **kwa)
    rt.save()

    # update anti-spam
    if len(cook) > RATINGS_MAX_COOKIE_LENGTH:
        cook = cook[1:]

    if request.user.is_authenticated():
        cook.append((ct.id, target.id))
        request.session[RATINGS_COOKIE_NAME] = cook
        request.user.message_set.create(message=_('Your rating was succesfully added.'))
    else:
        cook.append('%s:%s' % (ct.id, target.id))
        expores = datetime.strftime(datetime.utcnow() + timedelta(seconds=RATINGS_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(
                RATINGS_COOKIE_NAME,
                value=','.join(cook),
                max_age=RATINGS_MAX_COOKIE_AGE,
                expires=expores,
                path='/',
                domain=current_site.domain,
                secure=None
)

    return response


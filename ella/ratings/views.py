from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.utils import simplejson
from django.db import models

from ella.ratings.models import *

current_site = Site.objects.get_current()

UPDOWN = {'up' : 1, 'down' : -1}

def _get_cookie(request):
    """
    Returns cookie split by ','
    """
    try:
        return request.COOKIES[RATINGS_COOKIE_NAME].split(',')
    except KeyError:
        # Cookie not set
        return []

def get_was_rated(request, ct, target):
    """
    Returns whether object was rated by current user

    Rating can fail later on db query, this checks user cookies
    """
    if isinstance(ct, ContentType):
        ct = ct.id
    if isinstance(target, models.Model):
        target = target.pk
    return '%s:%s' % (ct, target) in _get_cookie(request)

def set_was_rated(request, response, ct, target):
    """
    Marks target as rated

    Adds object content_type and id to RATINGS_COOKIE_NAME cookie
    """
    cook = _get_cookie(request)
    if len(cook) > RATINGS_MAX_COOKIE_LENGTH:
        cook = cook[1:]
    cook.append('%s:%s' % (ct.id, target.id))
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=RATINGS_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
    domain = settings.SESSION_COOKIE_DOMAIN
    response.set_cookie(RATINGS_COOKIE_NAME, value=','.join(cook),
            max_age=RATINGS_MAX_COOKIE_AGE, expires=expires,  path='/',
            domain=domain, secure=None)


def get_response(request, target, message=None):
    if (request.is_ajax()):
        json = simplejson.dumps({'message':message or _('Your rating was succesfully added.')})
        return HttpResponse(json)
    else:
        if message and request.user.is_authenticated():
            request.user.message_set.create(message=message)

        if 'next' in request.REQUEST and request.REQUEST['next'].startswith('/'):
            url = request.POST['next']
        elif hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(url)

def do_rate(request, ct, target, plusminus):

    if get_was_rated(request, ct, target):
        return get_response(request, target, _('You have already rated this object.'))

    kwa = {'amount' : ANONYMOUS_KARMA}
    if request.user.is_authenticated():
        kwa['user'] = request.user
        if getattr(settings, 'AUTH_PROFILE_MODULE', False):
            profile = request.user.get_profile()
            kwa['amount'] = getattr(profile, 'karma', INITIAL_USER_KARMA)

    kwa['amount'] *= plusminus

    kwa['ip_address'] = request.META.get('REMOTE_ADDR', None)

    # Do the rating
    # Rating will not be neccessary added but fail silently
    rt = Rating(target_ct_id=ct.id, target_id=target.id, **kwa)
    rt.save()

    response =  get_response(request, target, message=_('Your rating was succesfully added.'))
    set_was_rated(request, response, ct, target)
    return response

def rate(request, context):
    """
    View for ella custom urls

    Expects rating in POST
    """
    # TODO: how to use django forms together with  content_type and objct from context
    try:
        plusminus = Decimal(request.POST['rating'])
    except KeyError:
        raise Http404
    # Allow only ratings in <-1;1> interval
    plusminus = plusminus.max(Decimal("-1")).min(Decimal("1"))
    return do_rate(
        request,
        context['content_type'],
        context['object'],
        plusminus
    )


# This method is not used in the moment and untested so commented out...
#@require_POST
#def rate_post(request, plusminus=1):
#    """
#    Add a simple up/down vote for a given object.
#    redirect to object's get_absolute_url() on success.
#
#    More granularity can be achieved via setting plusminus to something else than +/-1.
#
#    Params:
#        plusminus: rating itself
#
#    Form data:
#        POST:
#            ella.ratings.forms.RateForm
#            next: url to redirect to after successful attempt
#
#    Raises:
#        Http404 if no content_type or model is associated with the given IDs
#    """
#    form = RateForm(request.POST)
#    if not form.is_valid():
#        raise Http404
#
#    ct = form.cleaned_data['content_type']
#    target = form.cleaned_data['target']
#
#    return do_rate(request, ct, target, plusminus)

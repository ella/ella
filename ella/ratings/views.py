from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.views.decorators.http import require_POST

from ella.ratings.models import *
from ella.ratings.forms import RateForm

current_site = Site.objects.get_current()


def do_rate(request, ct, target, plusminus):
    if 'next' in request.REQUEST and request.REQUEST['next'].startswith('/'):
        url = request.POST['next']
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
        if getattr(settings, 'AUTH_PROFILE_MODULE', False):
            profile = request.user.get_profile()
            kwa['amount'] = getattr(profile, 'karma', INITIAL_USER_KARMA)

    kwa['amount'] *= plusminus

    if request.META.has_key('REMOTE_ADDR'):
        kwa['ip_address'] = request.META['REMOTE_ADDR']

    # do the rating
    rt = Rating(target_ct_id=ct.id, target_id=target.id, **kwa)
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

@require_POST
def rate(request, plusminus=1):
    """
    Add a simple up/down vote for a given object.
    redirect to object's get_absolute_url() on success.

    More granularity can be achieved via setting plusminus to something else than +/-1.

    Params:
        plusminus: rating itself

    Form data:
        POST:
            ella.ratings.forms.RateForm
            next: url to redirect to after successful attempt

    Raises:
        Http404 if no content_type or model is associated with the given IDs
    """
    form = RateForm(request.POST)
    if not form.is_valid():
        raise Http404

    ct = form.cleaned_data['content_type']
    target = form.cleaned_data['target']

    return do_rate(request, ct, target, plusminus)

from django.template import RequestContext
from django.core.views.generic import list_detail
from django.http import Http404

from ella.core.cache.template_loader import render_to_response
from ella.reminders import library

# local cache for get_reminder()
REMINDER_MAPPING = {}


def get_reminder(slug):
    try:
        rem = REMINDER_MAPPING[slug]
    except KeyError:
        for model in library.reminders:
            if slug == slugify(model._meta.verbose_name_plural):
                rem = model
                REMINDER_MAPPING[slug] = rem
                break
        else:
            raise Http404
    return rem

def reminder_list(request):
    return render_to_response(
            '',
            {'reminders' : library.reminders},
            context_instance=RequestContext(request)
)

def reminder_instances_list(request, reminder_class):
    rem = get_reminder(reminder_class)
    return list_detail(request, queryset=rem.objects.all())

def reminder_detail(request, reminder_class, reminder):
    rem = get_reminder(reminder_class)
    ireminder = get_cached_object(reminder, slug=reminder)
    return render_to_response(
            '',
            {'object': ireminder},
            context_instance=RequestContext(request)
)

def reminder_unsubscribe(request, reminder_class, reminder):
    rem = get_reminder(reminder_class)
    ireminder = get_cached_object(reminder, slug=reminder)
    # TODO: translation to contact
    ireminder.subscribe(request.user)

def reminder_subscribe(request, reminder_class, reminder):
    rem = get_reminder(reminder_class)
    ireminder = get_cached_object(reminder, slug=reminder)
    ireminder.unsubscribe(request.user)

def event_detail(request, reminder_class, reminder, event, url_remainder=None):
    return render_to_response('', {}, context_instance=RequestContext(request))

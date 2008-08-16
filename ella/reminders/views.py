from django.template import RequestContext
from django.views.generic import list_detail
from django.http import Http404
from django.db.models import ObjectDoesNotExist

from ella.core.cache.template_loader import render_to_response, find_template
from ella.core.cache import get_cached_object_or_404
from ella.reminders.library import library

def get_reminder_or_404(slug):
    try:
        return library.get_reminder_class(slug)
    except ObjectDoesNotExist:
        raise Http404

def reminder_list(request):
    return render_to_response(
            'page/reminders/reminders.html',
            {'reminders' : library.reminders},
            context_instance=RequestContext(request)
)

def reminder_instances_list(request, reminder_class):
    rem = get_reminder_or_404(reminder_class)

    source, origin, template_name = find_template((
                'page/reminders/%s/reminder_list.html' % (reminder_class),
                'page/reminders/reminder_list.html',
)
)
    return list_detail.object_list(
            request,
            queryset=rem.objects.all(),
            template_name=template_name
)

def reminder_detail(request, reminder_class, reminder):
    rem = get_reminder_or_404(reminder_class)
    ireminder = get_cached_object_or_404(rem, slug=reminder)
    return render_to_response(
            (
                'page/reminders/%s/%s.html' % (reminder_class, reminder),
                'page/reminders/%s/reminder.html' % (reminder_class),
                'page/reminders/reminder.html',
),
            {'object': ireminder},
            context_instance=RequestContext(request)
)

#@login_required
def reminder_unsubscribe(request, reminder_class, reminder):
    rem = get_reminder_or_404(reminder_class)
    ireminder = get_cached_object_or_404(rem, slug=reminder)
    # TODO: translation to contact, perhaps just pass the request and have the model deal with it
    ireminder.subscribe(request.user)

#@login_required
def reminder_subscribe(request, reminder_class, reminder):
    rem = get_reminder_or_404(reminder_class)
    ireminder = get_cached_object_or_404(rem, slug=reminder)
    ireminder.unsubscribe(request.user)

def event_detail(request, reminder_class, reminder, event, url_remainder=None):
    rem = get_reminder_or_404(reminder_class)
    ireminder = get_cached_object_or_404(rem, slug=reminder)
    obj = ireminder.get_event(event)
    return render_to_response(
            (
                'page/reminders/%s/%s/event/%s.html' % (reminder_class, reminder, event),
                'page/reminders/%s/%s/event.html' % (reminder_class, reminder),
                'page/reminders/%s/event.html' % reminder_class,
                'page/reminders/event.html',
),
            {'object' : obj},
            context_instance=RequestContext(request)
)

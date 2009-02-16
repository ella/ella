from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext

from django.conf import settings

from ella.newman.models import DevMessage

def devmessage_list(request):
    """
    List of development messages.
    """

    ctx = {
        'messages': DevMessage.objects.all()
}

    return render_to_response(
        'newman/devmessage-list.html',
        ctx,
        context_instance=RequestContext(request)
)

def devmessage_detail(request, msg_id):
    """
    Detail of development message.
    """

    ctx = {
        'message': DevMessage.objects.get(pk=msg_id)
}

    return render_to_response(
        'newman/devmessage-detail.html',
        ctx,
        context_instance=RequestContext(request)
)

@require_POST
@staff_member_required
def err_report(request):

    if not settings.DEBUG and not request.is_ajax():
        raise Http404, 'Accepts only AJAX calls'

    u = get_user(request)
    s = request.POST.get('subj')
    m = request.POST.get('msg')

    if s and m:

        e = EmailMessage('Newman report: %s' % s, m,
                         from_email=u.email, to=settings.ERR_REPORT_RECIPIENTS)
        e.send()
        return HttpResponse(content=ugettext('Your report was sent.'), mimetype='text/plain', status=200)

    return HttpResponse(content=ugettext('Subject or message is empty.'), mimetype='text/plain', status=405)

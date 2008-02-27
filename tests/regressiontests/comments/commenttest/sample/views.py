from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from django.template import Context, loader

from commenttest.sample.models import Apple, Orange
from django.contrib.contenttypes.models import ContentType

from ella.comments.forms import CommentForm


def list_apples(request):
    ret = '<h1>%s</h1>' % Apple.__name__
    for a in Apple.objects.all():
        ret += '<a href="./%s/">%s</a>\n' % (a.color, str(a))
    return HttpResponse('<pre>\n%s</pre>\n' % ret)

def list_apple(request, id):
    apple = get_object_or_404(Apple, color=id)
    return render_to_response('sample/apple_detail.html', {'apple': apple})




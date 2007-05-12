from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

def no_login(request):
    """
    Simple view.
    """
    return HttpResponse('OK')

@login_required
def logged_only(request):
    """
    Simple view that requires user to be logged in.
    """
    return HttpResponse('Hello %s' % request.user)

@login_required
def post_data(request):
    """
    View that displays all parameters it received via POST.
    """
    return HttpResponse('\n'.join('%s: %s' % (key, request.POST[key]) for key in sorted(request.POST.keys())))

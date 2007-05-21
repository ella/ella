from django.http import HttpResponse
from django import newforms as forms
from django import template

from django.contrib.auth.decorators import login_required

from nc.auth.views import nc_login

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


class LoginForm(forms.Form):
    name = forms.CharField()
    pwd = forms.CharField(widget=forms.PasswordInput)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return nc_login(request, url=request.GET.get('next', '/logged/'), **form.cleaned_data)
    else:
        form = LoginForm(initial={'name' : request.GET.get('name', '')})
    return HttpResponse(template.Template('<form method="POST">{{form}}<input type="submit"></form>').render(template.Context({'form' : form})))

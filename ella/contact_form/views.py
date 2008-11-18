
from django.contrib.formtools.preview import FormPreview, AUTO_ID
from django.http import HttpResponseRedirect

from ella.contact_form.forms import MessageForm

class PostForm(FormPreview):

    preview_template = 'page/contact_form/preview.html'
    form_template = 'page/contact_form/form.html'

    def done(self, request, cleaned_data):
        f = self.form(request.POST, auto_id=AUTO_ID)
        m = f.save()
        m.send()
        if ("redir" in request.GET):
            return HttpResponseRedirect(request.GET["redir"])
        return HttpResponseRedirect("/")

post_form = PostForm(MessageForm)

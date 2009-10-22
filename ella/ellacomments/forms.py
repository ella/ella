from threadedcomments.forms import ThreadedCommentForm

from ella.core.models import Publishable

class EllaCommmentForm(ThreadedCommentForm):
    def get_comment_object(self):
        c = super(EllaCommmentForm, self).get_comment_object()
        if c.content_type.model_class() == Publishable:
            c.content_type = self.target_object.content_type
        return c



from django.contrib.contenttypes.generic import GenericInlineModelAdmin

from ella.ellacomments.models import CommentOptionsObject

class CommentOptionsGenericInline(GenericInlineModelAdmin):
    model = CommentOptionsObject

    max_num = 1
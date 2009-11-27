from ella import newman

from ella.ellacomments.models import CommentOptionsObject

class CommentOptionsGenericInline(newman.GenericStackedInline):
    ct_field = "target_ct"
    ct_fk_field = "target_id"
    model = CommentOptionsObject

    max_num = 1

MODELS_WITH_COMMENTS = ('articles.article', 'galleries.gallery',)

newman.site.append_inline(MODELS_WITH_COMMENTS, CommentOptionsGenericInline)

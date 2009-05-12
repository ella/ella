from ella import newman
from ella.attachments.models import Attachment, Type


class AttachmentOptions(newman.NewmanModelAdmin):
    list_display = ('name', 'type', 'created',)
    list_filter = ('type',)
    prepopulated_fields = {'slug' : ('name',)}
    rich_text_fields = {'small': ('description',)}
    raw_id_fields = ('photo',)

newman.site.register(Attachment, AttachmentOptions)
newman.site.register(Type)


from django import newforms as forms
from django.contrib.contenttypes.models import ContentType

class ContentTypeWidget(forms.Select):
    def __init__(self, target_id_name, attrs=None, *args, **kwargs):
        attrs = attrs and attrs.copy() or {}
        attrs['onChange'] = "setRelatedLookupUrl(this);"
        attrs['onLoad'] = "setRelatedLookupUrl(this);"
        attrs['id'] = 'ct_for_%s' % target_id_name
        super(ContentTypeWidget, self).__init__(attrs=attrs, *args, **kwargs)

    def render(self, name, value, attrs=None):
        output = [ super(ContentTypeWidget, self).render(name, value, attrs=attrs) ]
        output.append(
            '''<script>
            function setRelatedLookupUrl(sender) {
                var pole = new Array();
                %s
                document.getElementById('lookup_id_' + sender.id.replace(/ct_for_/, '')).href = pole[sender.value];
}
            </script>'''  % (
                '\n'.join('pole[%d] = "../../../%s/%s/";' % (c.id, c.app_label, c.model) for c in  ContentType.objects.all())
)
)
        return ''.join(output)

class ForeignKeyRawIdWidget(forms.TextInput):
    """
    A Widget for displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box.
    """
    def render(self, name, value, attrs=None):
        from django.conf import settings
        related_url = '#'
        attrs['class'] = 'vRawIdAdminField' # The JavaScript looks for this hook.
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="Lookup"></a>' % settings.ADMIN_MEDIA_PREFIX)
        return u''.join(output)


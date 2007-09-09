from django import template
from django.contrib.contenttypes.models import ContentType

from ella.photos.models import Photo, Format, FormatedPhoto
from ella.core.cache.utils import get_cached_object

register = template.Library()
FORMATED_PHOTO_CT = ContentType.objects.get_for_model(FormatedPhoto)
PHOTO_CT = ContentType.objects.get_for_model(Photo)
FORMAT_CT = ContentType.objects.get_for_model(Format)

class ImgTag(template.Node):
    def __init__(self, photo, format, var_name):
        self.photo, self.format, self.var_name = photo, format, var_name

    def render(self, context):
        if isinstance(self.photo, basestring):
            try:
                photo = template.resolve_variable(self.photo, context)
            except template.VariableDoesNotExist:
                return ''
            try:
                formated_photo = get_cached_object(FORMATED_PHOTO_CT, photo=photo, format=self.format)
            except FormatedPhoto.DoesNotExist:
                try:
                    formated_photo = FormatedPhoto.objects.create(photo=photo, format=self.format)
                except (IOError, SystemError):
                    context[self.var_name] = self.format.get_blank_img()
                    return ''
        else:
            formated_photo = self.photo

        context[self.var_name] = formated_photo
        return ''

@register.tag
def img(parser, token):
    """
    Ahoj

    Examples::

        {% img FORMAT for VAR as VAR_NAME %}
        {% img FORMAT with FIELD VALUE as VAR_NAME %}
    """
    bits = token.split_contents()

    if len(bits) < 2 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    try:
        format = get_cached_object(FORMAT_CT, name=bits[1])
    except Format.DoesNotExist:
        raise template.TemplateSyntaxError, "Format with name %r does not exist" % bits[1]

    if len(bits) == 6:
        # img FORMAT for VAR_NAME
        if bits[2] != 'for':
            raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %}"
        formated_photo = bits[3]
    elif len(bits) == 7:
        # img FORMAT with FIELD VALUE
        if bits[2] != 'with':
            raise template.TemplateSyntaxError, "{% img FORMAT with FIELD VALUE as VAR_NAME %}"
        try:
            photo = get_cached_object(PHOTO_CT, **{str(bits[3]) : bits[4]})
        except photo.DoesNotExist:
            raise template.TemplateSyntaxError, "Photo with %r of %r does not exist" % (bits[3],  bits[4])

        try:
            formated_photo = get_cached_object(FORMATED_PHOTO_CT, photo=photo, format=format)
        except FormatedPhoto.DoesNotExist:
            formated_photo = FormatedPhoto.objects.create(photo=photo, format=format)
    else:
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    return ImgTag(formated_photo, format, bits[-1])



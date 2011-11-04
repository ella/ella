import logging

from django import template
from django.conf import settings
from django.db import IntegrityError

from ella.photos.models import Photo, Format, FormatedPhoto
from ella.core.cache.utils import get_cached_object

log = logging.getLogger('ella.photos')

register = template.Library()

class ImgTag(template.Node):
    def __init__(self, photo, format, var_name):
        self.photo, self.format, self.var_name = photo, format, var_name

    def render(self, context):
        if isinstance(self.photo, basestring):
            try:
                photo = template.Variable(self.photo).resolve(context)
                if not photo:
                    return ''
            except template.VariableDoesNotExist:
                return ''
            try:
                formated_photo = get_cached_object(FormatedPhoto, photo=photo, format=self.format)
            except FormatedPhoto.DoesNotExist:
                try:
                    formated_photo = FormatedPhoto.objects.create(photo=photo, format=self.format)
                except (IOError, SystemError, IntegrityError), e:
                    log.error("Cannot create formatted photo: %s" % e)
                    context[self.var_name] = self.format.get_blank_img()
                    return ''
        else:
            formated_photo = self.photo

        context[self.var_name] = formated_photo
        return ''

@register.tag
def img(parser, token):
    """
    Examples:

        {% img FORMAT for VAR as VAR_NAME %}
        {% img FORMAT with FIELD VALUE as VAR_NAME %}
    """
    bits = token.split_contents()

    if len(bits) < 2 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    try:
        format = get_cached_object(Format, name=bits[1], sites__id=settings.SITE_ID)
    except Format.DoesNotExist:
        logmsg = "Format with name %r does not exist (for site id %d)" % (bits[1], settings.SITE_ID)
        log.error(logmsg)

        if not settings.TEMPLATE_DEBUG:
            return template.Node()

        raise template.TemplateSyntaxError(logmsg)

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
            photo = get_cached_object(Photo, **{str(bits[3]) : bits[4]})
        except photo.DoesNotExist:
            raise template.TemplateSyntaxError, "Photo with %r of %r does not exist" % (bits[3],  bits[4])

        try:
            formated_photo = get_cached_object(FormatedPhoto, photo=photo, format=format)
        except FormatedPhoto.DoesNotExist:
            formated_photo = FormatedPhoto.objects.create(photo=photo, format=format)
    else:
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    return ImgTag(formated_photo, format, bits[-1])



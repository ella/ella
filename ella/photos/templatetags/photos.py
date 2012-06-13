import logging

from django import template
from django.conf import settings

from ella.photos.models import Photo, Format, FormatedPhoto
from ella.core.cache.utils import get_cached_object

log = logging.getLogger('ella.photos')

register = template.Library()

class ImageTag(template.Node):
    #{% image <photo_variable> in "format" as foobar %}
    def __init__(self, format, photo, var_name):
        self.format, self.photo, self.var_name = format, photo, var_name

    def render(self, context):
        if isinstance(self.format, template.Variable):
            try:
                format = self.format.resolve(context)
                if isinstance(format, basestring):
                    format = Format.objects.get_for_name(format)
            except (template.VariableDoesNotExist, Format.DoesNotExist):
                context[self.var_name] = None
                return ''
        else:
            format = self.format

        try:
            # try retrieving just the ID first to avoid DB lookup
            photo = template.Variable(self.photo + '_id').resolve(context)
        except template.VariableDoesNotExist:
            try:
                photo = template.Variable(self.photo).resolve(context)
            except template.VariableDoesNotExist:
                context[self.var_name] = None
                return ''

        formated_photo = FormatedPhoto.objects.get_photo_in_format(photo, format)
        context[self.var_name] = formated_photo
        return ''

def _parse_image(bits):
    if len(bits) != 6 or bits[2] != 'in' or bits[4] != 'as':
        raise template.TemplateSyntaxError('{% image <photo_variable> in "format" as foobar %}')

    format = template.Variable(bits[3])
    if format.literal is not None:
        try:
            format = Format.objects.get_for_name(format.literal)
        except Format.DoesNotExist:
            logmsg = "Format with name %r does not exist (for site id %d)" % (format.literal, settings.SITE_ID)
            log.error(logmsg)

            if not settings.TEMPLATE_DEBUG:
                return template.Node()

            raise template.TemplateSyntaxError(logmsg)

    return ImageTag(format, bits[1], bits[5])

@register.tag
def image(parser, token):
    """

    Generates thumbnails for ``Photo`` instances.

    syntax::

        {% image <photo> in <format> as <var_name> %}

    examples::

        {% image article.photo in "thumbnail" as thumb %}
        {% image article.photo in thumb_format as thumb %}

    """
    bits = token.split_contents()
    return _parse_image(bits)

class ImgTag(template.Node):
    def __init__(self, photo, format, var_name):
        self.photo, self.format, self.var_name = photo, format, var_name

    def render(self, context):
        if isinstance(self.photo, basestring):
            try:
                # try retrieving just the ID first to avoid DB lookup
                photo = template.Variable(self.photo + '_id').resolve(context)
            except template.VariableDoesNotExist:
                try:
                    photo = template.Variable(self.photo).resolve(context)
                except template.VariableDoesNotExist:
                    context[self.var_name] = None
                    return ''

            if not photo:
                context[self.var_name] = None
                return ''

            formated_photo = FormatedPhoto.objects.get_photo_in_format(photo, self.format)
        else:
            formated_photo = self.photo

        context[self.var_name] = formated_photo
        return ''

@register.tag
def img(parser, token):
    """

    Deprecated, use {% image %} instead. Generates thumbnails for ``Photo`` instances.

    syntax::

        {% img <format> for <var> as <var_name> %}
        {% img <format> with <field_value> as <var_name> %} 

    examples::

        {% img category_listing for object.photo as thumb %}
        {% img category_listing with pk 1150 as thumb %}

    """
    log.warning('You are using the deprecated {% img %} tag. please upgrade to {% image %}.')
    bits = token.split_contents()
    return _parse_img(bits)

def _parse_img(bits, legacy=True):
    if len(bits) < 2 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    try:
        format = Format.objects.get_for_name(bits[1])
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
            raise template.TemplateSyntaxError, "Photo with %r of %r does not exist" % (bits[3], bits[4])

        formated_photo = FormatedPhoto.objects.get_photo_in_format(photo, format)
    else:
        raise template.TemplateSyntaxError, "{% img FORMAT for VAR as VAR_NAME %} or {% img FORMAT with FIELD VALUE as VAR_NAME %}"

    return ImgTag(formated_photo, format, bits[-1])


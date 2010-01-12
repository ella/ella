import hashlib
from httplib import urlsplit

from django.conf import settings
from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

register = template.Library()

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

class PublishableFullUrlNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        publishable = template.Variable(self.var_name).resolve(context)
        return publishable.get_absolute_url(domain=True)


@register.tag
def publishable_full_url(parser, token):
    tokens = token.split_contents()
    if len(tokens) != 2:
        raise AttributeError('publishable_full_url takes one argument (variable containing publishable object).')
    var_name = tokens[1]
    return PublishableFullUrlNode(var_name)

class AtomIdNode(template.Node):
    def __init__(self, var_name, hashed_output):
        self.var_name = var_name
        self.hashed_output = hashed_output

    def render(self, context):
        """ 
        Example output: tag:zena.cz,2004-05-27:/12/10245 
        2004-05-27 ... publication date
        12 ... content type
        10245 ... publishable ID

        If self.hashed_output is set, whole tag is hashed by SHA1.
        """
        publishable = template.Variable(self.var_name).resolve(context)
        if publishable.publish_from:
            pub_date = publishable.publish_from.strftime('%Y-%m-%d')
        else:
            pub_date = '1970-01-01'
        url = publishable.get_absolute_url(domain=True)
        url_splitted = urlsplit(url)
        out = 'tag:%s,%s:/%d/%d' % (
            url_splitted.netloc,
            pub_date,
            publishable.content_type_id,
            publishable.pk
        )
        if self.hashed_output:
            h = hashlib.sha1(out)
            out = h.hexdigest()
        return out

@register.tag
def get_atom_id(parser, token):
    """
    Gets Atom ID for Publishable object.

    Example:
    {% get_atom_id publishable_object_template_variable %}          # outputs Atom ID value
    {% get_atom_id publishable_object_template_variable  hashed %}  # outputs hashed Atom ID value
    """
    hashed = False
    tokens = token.split_contents()
    if len(tokens) not in (2, 3,):
        raise AttributeError('get_atom_id takes one or two arguments (variable containing publishable object, [hashed]).')
    if len(tokens) == 3:
        if tokens[2].lower() == 'hashed':
            hashed = True

    var_name = tokens[1]
    return AtomIdNode(var_name, hashed)

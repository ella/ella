# -*- coding: utf-8 -*-
import hashlib
import random
from datetime import datetime
from httplib import urlsplit

from django.conf import settings
from django import template
from django.utils.feedgenerator import rfc2822_date

from ella.ellaexports.conf import ellaexports_settings

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

class FeedStrftimeNode(template.Node):
    def __init__(self, var_name, formatstring):
        self.var_name = var_name
        self.formatstring = formatstring

    def render(self, context):
        if self.var_name == 'None':
            variable = datetime.now()
        else:
            variable = template.Variable(self.var_name).resolve(context)
        if type(variable) != datetime:
            raise AttributeError('Given variable is not datetime object. %s' % variable)

        formatstring = ellaexports_settings.FEED_DATETIME_FORMAT
        if self.formatstring:
            formatstring = self.formatstring
        return variable.strftime(str(formatstring))

@register.tag
def feed_strftime(parser, token):
    """
    Gets datetime formated by custom format string.
    """
    formatstring = None
    tokens = token.split_contents()
    if len(tokens) not in (2, 3,):
        raise AttributeError('get_atom_id takes one or two arguments (variable containing publishable object, [hashed]).')
    if len(tokens) == 3:
        formatstring = tokens[2]
        if formatstring[0] in ('\'', '"',):
            formatstring = formatstring[1:]
        if formatstring[-1] in ('\'', '"',):
            formatstring = formatstring[:-1]

    var_name = tokens[1]
    return FeedStrftimeNode(var_name, formatstring)

@register.filter
def feed_replace_datetime_czech(value):
    EN2CZ_MONTHS = {
        'January': u'leden',
        'February': u'únor',
        'March': u'březen',
        'April': u'duben',
        'May': u'květen',
        'June': u'červen',
        'July': u'červenec',
        'August': u'srpen',
        'September': u'září',
        'October': u'říjen',
        'November': u'listopad',
        'December': u'prosinec',
    }
    EN2CZ_WEEKDAYS = {
        'Monday': u'pondělí',
        'Tuesday': u'úterý',
        'Wednesday': u'středa',
        'Thursday': u'čtvrtek',
        'Friday': u'pátek',
        'Saturday': u'sobota',
        'Sunday': u'neděle',
    }
    out = value
    first_pass = ''
    for en, cz in EN2CZ_MONTHS.items():
        if value.find(en) > -1:
            first_pass = value.replace(en, cz)
            break
    for en, cz in EN2CZ_WEEKDAYS.items():
        if first_pass.find(en) > -1:
            out = first_pass.replace(en, cz)
            break
    return out

@register.filter
def shuffle(value):
    result = list(value)
    random.shuffle(result)
    return result

register.filter(rfc2822_date)

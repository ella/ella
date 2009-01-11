"""
Oldforms validators for tagging related fields - these are still
required for basic ``django.contrib.admin`` application field validation
until the ``newforms-admin`` branch lands in trunk.
"""
from django.utils.translation import ugettext as _
from django.forms.util import ValidationError

from ella.tagging import settings
from ella.tagging.utils import parse_tag_input

def isTagList(field_data, all_data):
    """
    Validates that ``field_data`` is a valid list of tags.
    """
    for tag_name in parse_tag_input(field_data):
        if len(tag_name) > settings.MAX_TAG_LENGTH:
            raise ValidationError(
                _('Each tag may be no more than %s characters long.') % settings.MAX_TAG_LENGTH)

def isTag(field_data, all_data):
    """
    Validates that ``field_data`` is a valid tag.
    """
    tag_names = parse_tag_input(field_data)
    if len(tag_names) > 1:
        raise ValidationError(_('Multiple tags were given.'))
    elif len(tag_names[0]) > settings.MAX_TAG_LENGTH:
        raise ValidationError(
            _('A tag may be no more than %s characters long.') % settings.MAX_TAG_LENGTH)

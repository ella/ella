# -*- coding: UTF-8 -*-
"""
Common text processing functions.
"""
import unicodedata


def __unicode_to_ascii(text):
    """ discards diacritical marks from unicode text """
    line = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in line if not unicodedata.combining(c))

def cz_compare(a, b):
    """ a, b parameters should be strings or unicodes. """
    ma = __unicode_to_ascii(unicode(a))
    mb = __unicode_to_ascii(unicode(b))
    return cmp(ma, mb)

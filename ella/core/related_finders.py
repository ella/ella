'''
Created on 1.2.2012

@author: xaralis
'''
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Publishable

def fillup_from_category(related, obj, count, mods=[], only_from_same_site=True):
    """
    Given a ``related`` list, fills that list up to the ``count`` by top objects
    listed in same category as ``obj``.
    """
    if len(related) >= count:
        return related

    count -= len(related)

    # top objects in given category
    if count > 0:
        from ella.core.models import Listing
        cat = obj.category
        listings = Listing.objects.get_listing(category=cat, count=count + len(related), mods=mods)
        for l in listings:
            t = l.target
            if t != obj and t not in related:
                related.append(t)
                count -= 1

            if count <= 0:
                return related

    return related


def related_only(obj, count, mods=[], only_from_same_site=True):
    """
    Returns objects related to ``obj`` up to ``count`` by searching 
    ``Related`` instances for the ``obj``. 
    """
    # manually entered dependencies
    qset = Publishable.objects.filter(
        related__related_ct=ContentType.objects.get_for_model(obj),
        related__related_id=obj.pk
    )
    if mods:
        qset = qset.filter(content_type__in=[
            ContentType.objects.get_for_model(m).pk for m in mods])
    if only_from_same_site:
        qset = qset.filter(category__site__pk=settings.SITE_ID)
    return list(qset[:count])


def related_and_category(obj, count, mods=[], only_from_same_site=True):
    """
    Returns objects related to ``obj`` up to ``count`` by searching 
    ``Related`` instances for the ``obj`` and filling up missing items
    from top objects listed in same category as ``obj``.
    """
    related = related_only(obj, count, mods, only_from_same_site)
    return fillup_from_category(related, obj, count, mods, only_from_same_site)



from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Publishable


def related_by_category(obj, count, collected_so_far, mods=[], only_from_same_site=True):
    """
    Returns other Publishable objects related to ``obj`` by using the same
    category principle. Returns up to ``count`` objects.
    """
    related = []
    # top objects in given category
    if count > 0:
        from ella.core.models import Listing
        cat = obj.category
        listings = Listing.objects.get_queryset_wrapper(
            category=cat,
            content_types=[ContentType.objects.get_for_model(m) for m in mods]
        )
        for l in listings[0:count + len(related)]:
            t = l.publishable
            if t != obj and t not in collected_so_far and t not in related:
                related.append(t)
                count -= 1

            if count <= 0:
                return related
    return related


def directly_related(obj, count, collected_so_far, mods=[], only_from_same_site=True):
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




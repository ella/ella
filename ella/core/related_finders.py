from django.contrib.contenttypes.models import ContentType
from ella.core.cache.utils import get_cached_objects, SKIP

from ella.core.models import Related


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
    qset = Related.objects.filter(publishable=obj)

    if mods:
        qset = qset.filter(related_ct__in=[
            ContentType.objects.get_for_model(m).pk for m in mods])

    return get_cached_objects(qset.values_list('related_ct', 'related_id')[:count], missing=SKIP)




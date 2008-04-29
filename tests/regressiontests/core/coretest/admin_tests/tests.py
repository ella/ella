placements = r'''
>>> from django.contrib import admin
>>> from django.utils.datastructures import MultiValueDict
>>> from ella.core.models import Placement
>>> from ella.core.admin import PlacementInlineOptions
>>> from coretest.admin_tests.models import SampleAdminObject, EmptyAdminObject

>>> empty_data = MultiValueDict({
...     "core-placement-target_ct-target_id-TOTAL_FORMS": ["2"],
...     "core-placement-target_ct-target_id-INITIAL_FORMS": ["0"],
...
...     "core-placement-target_ct-target_id-0-category": [""],
...     "core-placement-target_ct-target_id-0-publish_from_0": [""],
...     "core-placement-target_ct-target_id-0-publish_from_1": [""],
...     "core-placement-target_ct-target_id-0-publish_to_0": [""],
...     "core-placement-target_ct-target_id-0-publish_to_1": [""],
...     "core-placement-target_ct-target_id-0-slug": [""],
...     "core-placement-target_ct-target_id-0-static": [""],
...     "core-placement-target_ct-target_id-0-listings": [],
...
...     "core-placement-target_ct-target_id-1-category": [""],
...     "core-placement-target_ct-target_id-1-publish_from_0": [""],
...     "core-placement-target_ct-target_id-1-publish_from_1": [""],
...     "core-placement-target_ct-target_id-1-publish_to_0": [""],
...     "core-placement-target_ct-target_id-1-publish_to_1": [""],
...     "core-placement-target_ct-target_id-1-slug": [""],
...     "core-placement-target_ct-target_id-1-static": [""],
...     "core-placement-target_ct-target_id-1-listings": [],
...})

# disable pre-filling current date to publish_from
>>> Placement._meta.get_field('publish_from').default=None

>>> sao1 = SampleAdminObject.objects.get(pk=1)

>>> pio = PlacementInlineOptions(SampleAdminObject, admin.site)
>>> pif = pio.get_formset(None)
>>> pifi = pif(data=empty_data, files={}, instance=sao1)
>>> pifi.is_valid()
True
>>> pifi.cleaned_data
[{}, {}]


# create first placement
>>> data = empty_data.copy()
>>> data.update(MultiValueDict({
...     "core-placement-target_ct-target_id-0-category": ["1"],
...     "core-placement-target_ct-target_id-0-publish_from_0": ["2007-07-01"],
...     "core-placement-target_ct-target_id-0-publish_from_1": ["00:00:00"],
...}))
>>> pifi = pif(data=data, files={}, instance=sao1)
>>> pifi.is_valid()
True
>>> pifi.errors
[{}, {}]
>>> pifi.cleaned_data
[{'category': <Category: example.com/>, 'publish_from': datetime.datetime(2007, 7, 1, 0, 0), 'listings': [], 'publish_to': None, 'id': None, 'static': False, 'slug': u''}, {}]
>>> objs = pifi.save()
>>> placement = objs[0]
>>> placement.slug
u'sample1'
>>> sao1.get_absolute_url()
'/2007/7/1/sample-admin-objects/sample1/'
'''

__test__ = {
    'placements' : placements,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()


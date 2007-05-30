rating = r'''
>>> from nc.ratings.models import *
>>> Rating.objects.count()
0

>>>
>>> from rate_simple.models import *
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_obj.owner.id
1

# rating on not-rated object:
>>> Rating.objects.get_for_object(cheap_obj)
0

# store content_types for further use
>>> from django.contrib.contenttypes.models import ContentType
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_ct = ContentType.objects.get_for_model(ExpensiveSampleModel)

>>> from django.test import Client
>>> cl = Client()

# rate cheap model up anonymously
>>> resp = cl.get('/ratings/rate/%s/%s/up/' % (cheap_ct.id, cheap_obj.id))
>>> resp.status_code
302
>>> Rating.objects.get_for_object(cheap_obj) == ANONYMOUS_KARMA
True
>>> csm = CheapSampleModel.rated.all()[0]
>>> csm.rating == ANONYMOUS_KARMA
True
>>> resp = cl.get('/ratings/rate/%s/%s/down/' % (cheap_ct.id, cheap_obj.id))
>>> resp.status_code
302

# blocked by anti-spam
>>> Rating.objects.get_for_object(cheap_obj) == ANONYMOUS_KARMA
True

# start with new client to erase cookie
>>> cl = Client()
>>> resp = cl.get('/ratings/rate/%s/%s/down/' % (cheap_ct.id, cheap_obj.id))
>>> resp.status_code
302
>>> Rating.objects.get_for_object(cheap_obj)
0
>>> Rating.objects.count()
2
>>> csm = CheapSampleModel.rated.all()[0]
>>> csm.rating
0
'''

template_tags = r'''
>>> from nc.ratings.models import *
>>> from rate_simple.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> from django.template import Template, Context
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)

>>> t = Template('{% load ratings.tags %}{% rating for obj as rating %}{{rating}}')
>>> t.render(Context({'obj' : cheap_obj}))
'0'
>>> r = Rating(target_ct=cheap_ct, target_id=cheap_obj.id, amount=6)
>>> r.save()
>>> t.render(Context({'obj' : cheap_obj}))
'6'
>>> t = Template('{% load ratings.tags %}{% rate_urls for obj as rate_up rate_down %}{{rate_up}} {{rate_down}}')
>>> t.render(Context({'obj' : cheap_obj})) == '/ratings/rate/%(ct_id)s/%(obj_id)s/up/ /ratings/rate/%(ct_id)s/%(obj_id)s/down/' % {
...     'obj_id' : cheap_obj.id,
...     'ct_id' : cheap_ct.id
...}
True
>>> t = Template('{% load ratings.tags %}{% top_rated 5 as top %}{{top}}')
>>> t.render(Context())
'[(<CheapSampleModel: CheapSampleModel object>, 6)]'

>>> t = Template('{% load ratings.tags %}{% top_rated 5 rate_simple.expensivesamplemodel as top %}{{top}}')
>>> t.render(Context())
'[]'

>>> t = Template('{% load ratings.tags %}{% top_rated 5 rate_simple.expensivesamplemodel rate_simple.cheapsamplemodel as top %}{{top}}')
>>> t.render(Context())
'[(<CheapSampleModel: CheapSampleModel object>, 6)]'

>>> r.delete()
'''

top_objects = r'''
>>> from rate_simple.models import *
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> expensive_obj = ExpensiveSampleModel.objects.all()[0]

>>> from django.contrib.contenttypes.models import ContentType

# store content_types for further use
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_ct = ContentType.objects.get_for_model(expensive_obj)

# clear all ratings and create new ones
>>> from nc.ratings.models import Rating
>>> Rating.objects.all().delete()
>>> r = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r.save()
>>> r = Rating(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2)
>>> r.save()

>>> Rating.objects.get_top_objects(2)
[(<ExpensiveSampleModel: ExpensiveSampleModel object>, 2), (<CheapSampleModel: CheapSampleModel object>, 1)]

>>> Rating.objects.get_top_objects(1, [CheapSampleModel])
[(<CheapSampleModel: CheapSampleModel object>, 1)]
>>> Rating.objects.get_top_objects(10, [ExpensiveSampleModel, CheapSampleModel])
[(<ExpensiveSampleModel: ExpensiveSampleModel object>, 2), (<CheapSampleModel: CheapSampleModel object>, 1)]
'''
__test__ = {
    'rating' : rating,
    'template_tags' : template_tags,
    'top_objects' : top_objects,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()


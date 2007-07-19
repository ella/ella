rating = r'''
>>> from ella.ratings.models import *
>>> Rating.objects.all().delete()
>>> Rating.objects.count()
0

>>>
>>> from rate_simple.models import *
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_obj.owner.id
1

# rating on not-rated object:
>>> int(Rating.objects.get_for_object(cheap_obj))
0

# store content_types for further use
>>> from django.contrib.contenttypes.models import ContentType
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_ct = ContentType.objects.get_for_model(ExpensiveSampleModel)

>>> from django.test import Client
>>> cl = Client()

# rate cheap model up anonymously
>>> resp = cl.post('/ratings/rate/up/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> resp.status_code
302
>>> Rating.objects.get_for_object(cheap_obj) == ANONYMOUS_KARMA
True
>>> csm = CheapSampleModel.rated.all()[0]
>>> csm.rating == ANONYMOUS_KARMA
True
>>> resp = cl.post('/ratings/rate/down/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> resp.status_code
302

# blocked by anti-spam
>>> Rating.objects.get_for_object(cheap_obj) == ANONYMOUS_KARMA
True

# start with new client to erase cookie
>>> cl = Client()
>>> resp = cl.post('/ratings/rate/down/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> resp.status_code
302
>>> int(Rating.objects.get_for_object(cheap_obj))
0
>>> Rating.objects.count()
2
>>> csm = CheapSampleModel.rated.all()[0]
>>> int(csm.rating)
0
'''

template_tags = r'''
>>> from ella.ratings.models import *
>>> from rate_simple.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> from django.template import Template, Context
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)

# clear all ratings and create new ones
>>> Rating.objects.all().delete()

>>> t = Template('{% load ratings %}{% rating for obj as rating %}{{rating}}')
>>> t.render(Context({'obj' : cheap_obj}))
u'0'
>>> r = Rating(target_ct=cheap_ct, target_id=cheap_obj.id, amount=6)
>>> r.save()
>>> t.render(Context({'obj' : cheap_obj}))
u'6'
>>> t = Template('{% load ratings %}{% rate_form for obj as rate_form rate_up rate_down %}{{rate_form}} {{rate_up}} {{rate_down}}')
>>> t.render(Context({'obj' : cheap_obj})) == u'<input type="hidden" name="content_type" value="%s" id="id_content_type" /><input type="hidden" name="target" value="%s" id="id_target" /> /ratings/rate/up/ /ratings/rate/down/' % (cheap_ct.id, cheap_obj.id)
True
>>> t = Template('{% load ratings %}{% top_rated 5 as top %}{% for rat in top %}{{rat.0}}: {{rat.1}}\n{% endfor %}')
>>> t.render(Context())
u'CheapSampleModel object: 6\n'

>>> t = Template('{% load ratings %}{% top_rated 5 rate_simple.expensivesamplemodel as top %}{{top}}')
>>> t.render(Context())
u'[]'

>>> t = Template('{% load ratings %}{% top_rated 5 rate_simple.expensivesamplemodel rate_simple.cheapsamplemodel as top %}{% for rat in top %}{{rat.0}}: {{rat.1}}\n{% endfor %}')
>>> t.render(Context())
u'CheapSampleModel object: 6\n'

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
>>> from ella.ratings.models import Rating
>>> Rating.objects.all().delete()
>>> r = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r.save()
>>> r2 = Rating(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2)
>>> r2.save()

>>> [ (str(obj), int(rat)) for obj, rat in Rating.objects.get_top_objects(2) ]
[('ExpensiveSampleModel object', 2), ('CheapSampleModel object', 1)]

>>> [ (str(obj), int(rat)) for obj, rat in Rating.objects.get_top_objects(1, [CheapSampleModel]) ]
[('CheapSampleModel object', 1)]
>>> [ (str(obj), int(rat)) for obj, rat in Rating.objects.get_top_objects(10, [ExpensiveSampleModel, CheapSampleModel]) ]
[('ExpensiveSampleModel object', 2), ('CheapSampleModel object', 1)]

# cleanup
>>> r.delete()
>>> r2.delete()
>>> r = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r.save()
>>> r2 = Rating(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2)
>>> r2.save()
'''

karma = r'''
# imports
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.ratings.models import Rating, INITIAL_USER_KARMA
>>> from rate_simple.models import *
>>> from django.test import Client

# clear all ratings and create new ones
>>> Rating.objects.all().delete()

# get objects to rate
>>> cheap_obj = CheapSampleModel.rated.all()[0]
>>> int(cheap_obj.rating)
0
>>> expensive_obj = ExpensiveSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_ct = ContentType.objects.get_for_model(expensive_obj)

# login via test client
>>> cl = Client()
>>> cl.login(username="rater", password="admin")
True

# rate some objects, check that the rating amount is the same as user's karma
>>> cl.post('/ratings/rate/up/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id}).status_code
302
>>> up = UserProfile.objects.get(user__username='rater')
>>> up.karma
5
>>> int(Rating.objects.get_for_object(cheap_obj))
5
>>> cl = Client()
>>> cl.login(username="rater2", password="admin")
True
>>> up.save()
>>> cl.post('/ratings/rate/up/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id}).status_code
302
>>> int(Rating.objects.get_for_object(cheap_obj))
15
>>> cl.post('/ratings/rate/up/', {'content_type' : expensive_ct.id, 'target' : expensive_obj.id}).status_code
302

# recalculate the karma
>>> from ella.ratings import karma
>>> karma.recalculate_karma()
True
>>> up = UserProfile.objects.get(user__username='rater2')
>>> up.karma == INITIAL_USER_KARMA
True
>>> up = UserProfile.objects.get(user__username='owner')
>>> up.karma > INITIAL_USER_KARMA
True
'''

rate_form = r'''
>>> from ella.ratings.forms import RateForm
>>> from ella.ratings.models import Rating
>>> from rate_simple.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> cheap_obj = CheapSampleModel.rated.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)

# ideal case
>>> form = RateForm({'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> form.is_valid()
True
>>> cheap_obj == form.cleaned_data['target']
True
>>> cheap_ct == form.cleaned_data['content_type']
True

# bad data
>>> form = RateForm({'content_type' : cheap_ct.id, 'target' : 0})
>>> form.is_valid()
False
>>> form.errors
{'target': [u'The given target object does not exist.']}

'''

__test__ = {
    'rate_form' : rate_form,
    'rating' : rating,
    'template_tags' : template_tags,
    'top_objects' : top_objects,
    'karma' : karma,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()


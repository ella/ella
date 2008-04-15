rating = r'''
>>> from ella.ratings.models import *
>>> Rating.objects.all().delete()
>>> TotalRate.objects.all().delete()
>>> Rating.objects.count()
0
>>> TotalRate.objects.count()
0

>>> from rate_simple.models import *
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_obj.owner.id
1

# rating on not-rated object:
>>> int(TotalRate.objects.get_total_rating(cheap_obj))
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
>>> TotalRate.objects.get_total_rating(cheap_obj) == ANONYMOUS_KARMA*RATINGS_COEFICIENT
True
>>> resp = cl.post('/ratings/rate/down/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> resp.status_code
302

# blocked by anti-spam
>>> TotalRate.objects.get_total_rating(cheap_obj) == ANONYMOUS_KARMA*RATINGS_COEFICIENT
True

# start with new client to erase cookie
>>> cl = Client()
>>> resp = cl.post('/ratings/rate/down/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id})
>>> resp.status_code
302
>>> int(TotalRate.objects.get_total_rating(cheap_obj))
0
>>> Rating.objects.count()
2
'''

template_tags = r'''
>>> from ella.ratings.models import *
>>> from rate_simple.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> from django.template import Template, Context
>>> expansive_obj = ExpensiveSampleModel.objects.all()[0]
>>> expansive_ct = ContentType.objects.get_for_model(expansive_obj)
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)

# clear all ratings and create new ones
>>> Rating.objects.all().delete()
>>> TotalRate.objects.all().delete()

>>> t = Template('{% load ratings %}{% rating for obj as rating %}{{rating}}')
>>> t.render(Context({'obj' : expansive_obj}))
u'0.0'
>>> r = Rating(target_ct=expansive_ct, target_id=expansive_obj.id, amount=6)
>>> r.save()
>>> r2 = Rating(target_ct=cheap_ct, target_id=cheap_obj.id, amount=4)
>>> r2.save()
>>> tr = TotalRate(target_ct=expansive_ct, target_id=expansive_obj.id, amount=10)
>>> tr.save()
>>> t.render(Context({'obj' : expansive_obj}))
u'16.6'
>>> t = Template('{% load ratings %}{% rate_urls for obj as up down %}{{up}} {{down}}')
>>> t.render(Context({'obj' : expansive_obj})) == u'%(url)srate/up/ %(url)srate/down/' % {'url' : expansive_obj.get_absolute_url(),}
True
>>> t = Template('{% load ratings %}{% rate_urls for obj as rate_form rate_up rate_down %}{{rate_form}} {{rate_up}} {{rate_down}}')
>>> t.render(Context({'obj' : cheap_obj})) == u'<input type="hidden" name="content_type" value="%s" id="id_content_type" /><input type="hidden" name="target" value="%s" id="id_target" /> /ratings/rate/up/ /ratings/rate/down/' % (cheap_ct.id, cheap_obj.id)
True
>>> t = Template('{% load ratings %}{% top_rated 5 as top %}{% for rat in top %}{{rat.0}}: {{rat.1}}\n{% endfor %}')
>>> t.render(Context())
u'ExpensiveSampleModel object: 16.6\nCheapSampleModel object: 4.4\n'

>>> r2.delete()
>>> t = Template('{% load ratings %}{% top_rated 5 rate_simple.cheapsamplemodel as top %}{{top}}')
>>> t.render(Context())
u'[]'

>>> t = Template('{% load ratings %}{% top_rated 5 rate_simple.cheapsamplemodel rate_simple.expensivesamplemodel as top %}{% for rat in top %}{{rat.0}}: {{rat.1}}\n{% endfor %}')
>>> t.render(Context())
u'ExpensiveSampleModel object: 16.6\n'

>>> r.delete()
>>> tr.delete()
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
>>> from ella.ratings.models import Rating, TotalRate
>>> Rating.objects.all().delete()
>>> TotalRate.objects.all().delete()
>>> r = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r.save()
>>> r2 = Rating(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2)
>>> r2.save()
>>> tr = TotalRate(target_id=cheap_obj.id, target_ct=cheap_ct, amount=3)
>>> tr.save()
>>> tr2 = TotalRate(target_id=expensive_obj.id, target_ct=expensive_ct, amount=4)
>>> tr2.save()

>>> [ (str(obj), int(rat)) for obj, rat in TotalRate.objects.get_top_objects(2) ]
[('ExpensiveSampleModel object', 6), ('CheapSampleModel object', 4)]

>>> [ (str(obj), int(rat)) for obj, rat in TotalRate.objects.get_top_objects(1, [CheapSampleModel]) ]
[('CheapSampleModel object', 4)]
>>> [ (str(obj), int(rat)) for obj, rat in TotalRate.objects.get_top_objects(10, [ExpensiveSampleModel, CheapSampleModel]) ]
[('ExpensiveSampleModel object', 6), ('CheapSampleModel object', 4)]

# cleanup
>>> r.delete()
>>> r2.delete()
>>> tr.delete()
>>> tr2.delete()
'''

aggregation = r'''
# imports
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.ratings.models import Agg, Rating, TotalRate, ANONYMOUS_KARMA, RATINGS_COEFICIENT
>>> from rate_simple.models import *

# clear all ratings and create new ones
>>> Rating.objects.all().delete()
>>> Agg.objects.all().delete()
>>> TotalRate.objects.all().delete()
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_obj = ExpensiveSampleModel.objects.all()[0]
>>> expensive_ct = ContentType.objects.get_for_model(expensive_obj)

>>> r = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r.save()
>>> r2 = Rating(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2)
>>> r2.save()
>>> r3 = Rating(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1)
>>> r3.save()

>>> Rating.objects.count()
3
>>> TotalRate.objects.get_total_rating(cheap_obj) == ANONYMOUS_KARMA*RATINGS_COEFICIENT + ANONYMOUS_KARMA*RATINGS_COEFICIENT
True

# aggregation data
>>> from ella.ratings import aggregation
>>> aggregation.transfer_data()
True
>>> Rating.objects.count()
3
>>> TotalRate.objects.get_total_rating(cheap_obj) == ANONYMOUS_KARMA*RATINGS_COEFICIENT + ANONYMOUS_KARMA*RATINGS_COEFICIENT
True
>>> Agg.objects.count()
0
>>> TotalRate.objects.count()
0
>>> a = Agg(target_id=cheap_obj.id, target_ct=cheap_ct, amount=4, time='2006-02-07', people=4, period='y')
>>> a.save()
>>> a2 = Agg(target_id=expensive_obj.id, target_ct=expensive_ct, amount=2, time='2006-02-07', people=2, period='y')
>>> a2.save()
>>> a3 = Agg(target_id=cheap_obj.id, target_ct=cheap_ct, amount=1, time='2006-05-07', people=1, period='y')
>>> a3.save()

>>> aggregation.transfer_data()
True
>>> Agg.objects.count()
2
>>> Rating.objects.count()
3
>>> TotalRate.objects.count()
2

# amount with time function in database
>>> trs = TotalRate.objects.all()[0]
>>> trs.amount
Decimal("0.20")
>>> trs2 = TotalRate.objects.all()[1]
>>> trs2.amount
Decimal("0.50")
>>> TotalRate.objects.get_total_rating(cheap_obj)
Decimal("2.7")
>>> TotalRate.objects.get_total_rating(expensive_obj)
Decimal("2.4")

# cleanup
>>> r.delete()
>>> r2.delete()
>>> r3.delete()
>>> a.delete()
>>> a2.delete()
>>> a3.delete()
>>> TotalRate.objects.all().delete()
'''

karma = r'''
# imports
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.ratings.models import Rating, TotalRate, INITIAL_USER_KARMA
>>> from rate_simple.models import *
>>> from django.test import Client

# clear all ratings and create new ones
>>> Rating.objects.all().delete()
>>> TotalRate.objects.all().delete()

# get objects to rate
>>> cheap_obj = CheapSampleModel.objects.all()[0]
>>> int(TotalRate.objects.get_total_rating(cheap_obj))
0
>>> expensive_obj = ExpensiveSampleModel.objects.all()[0]
>>> cheap_ct = ContentType.objects.get_for_model(cheap_obj)
>>> expensive_ct = ContentType.objects.get_for_model(expensive_obj)

# login via test client
>>> cl = Client()
>>> cl.login(username="rater", password="admin")
True

>>> tr = TotalRate(target_id=cheap_obj.id, target_ct=cheap_ct, amount=3)
>>> tr.save()
>>> tr2 = TotalRate(target_id=expensive_obj.id, target_ct=expensive_ct, amount=4)
>>> tr2.save()

# rate some objects, check that the rating amount is the same as user's karma
>>> cl.post('/ratings/rate/up/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id}).status_code
302
>>> up = UserProfile.objects.get(user__username='rater')
>>> up.karma
Decimal("5.0")
>>> TotalRate.objects.get_total_rating(cheap_obj)
Decimal("8.5")
>>> cl = Client()
>>> cl.login(username="rater2", password="admin")
True
>>> up.save()
>>> cl.post('/ratings/rate/up/', {'content_type' : cheap_ct.id, 'target' : cheap_obj.id}).status_code
302
>>> TotalRate.objects.get_total_rating(cheap_obj)
Decimal("19.5")
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
>>> up.karma
Decimal("38.5")
'''

rate_form = r'''
>>> from ella.ratings.forms import RateForm
>>> from ella.ratings.models import Rating
>>> from rate_simple.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> cheap_obj = CheapSampleModel.objects.all()[0]
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

detail_urls = r'''
>>> from rate_simple.models import *
>>> expensive_obj = ExpensiveSampleModel.objects.all()[0]
>>> expensive_obj.get_absolute_url()
'/2007/7/1/expensive-sample-models/expensivesamplemodel-1/'

>>> from ella.ratings.models import Rating, TotalRate, ANONYMOUS_KARMA, RATINGS_COEFICIENT
>>> Rating.objects.all().delete()
>>> TotalRate.objects.all().delete()
>>> int(TotalRate.objects.get_total_rating(expensive_obj))
0
>>> from django.test import Client
>>> c = Client()
>>> response = c.get('/2007/7/1/expensive-sample-models/expensivesamplemodel-1/')
>>> response.status_code
200
>>> response.context['object'] == expensive_obj
True
>>> response = c.get('/2007/7/1/expensive-sample-models/expensivesamplemodel-1/rate/up/')
>>> response.status_code
302
>>> TotalRate.objects.get_total_rating(expensive_obj) == ANONYMOUS_KARMA*RATINGS_COEFICIENT
True
>>> c = Client()
>>> response = c.get('/2007/7/1/expensive-sample-models/expensivesamplemodel-1/rate/down/')
>>> response.status_code
302
>>> int(TotalRate.objects.get_total_rating(expensive_obj))
0
>>> c.get('/2007/7/1/expensive-sample-models/expensivesamplemodel-1/rate/').status_code
404
'''

__test__ = {
    'karma' : karma,
    'rating' : rating,
    #'aggregation' : aggregation,
    'template_tags' : template_tags,
    'top_objects' : top_objects,
    'rate_form' : rate_form,
    'detail_urls' : detail_urls,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()


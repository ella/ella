listing = r"""
>>> from ella.core.models import Listing, Category
>>> from django.template import Template, Context

>>> cat = Category.objects.get(pk=1)
>>> sub_cat = Category.objects.get(pk=2)
>>> c = Context({'category': cat, 'sub_category': sub_cat,})

almost same templates like in doc strings
-----------------------------------------

>>> t1 = Template('{% listing 2 of redir_sample.redirobject for "" as obj_list %}{{obj_list|safe}}')
>>> t1.render(c)
u'[<Listing: RedirObject object listed in example.com/>]'

>>> t2 = Template('{% listing 2 of redir_sample.redirobject for category as obj_list %}{{obj_list|safe}}')
>>> t2.render(c)
u'[<Listing: RedirObject object listed in example.com/>]'

>>> t3 = Template('{% listing 2 from 1 of redir_sample.redirobject as obj_list %}{{obj_list|safe}}')
>>> t3.render(c)
u'[<Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>]'



>>> t4 = Template('{% listing 10 of redir_sample.redirobject for category as obj_list %}{{obj_list|safe}}')
>>> t4.render(c)
u'[<Listing: RedirObject object listed in example.com/>]'

>>> t5 = Template('{% listing 10 of redir_sample.redirobject for category with children as obj_list %}{{obj_list|safe}}')
>>> t5.render(c)
u'[<Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>]'

>>> t6 = Template('{% listing 10 of redir_sample.redirobject for category with descendents as obj_list %}{{obj_list|safe}}')
>>> t6.render(c)
u'[<Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>, <Listing: RedirObject object listed in example.com/cat/subcat1>]'

>>> t7 = Template('{% listing 10 of redir_sample.redirobject for sub_category with descendents as obj_list %}{{obj_list|safe}}')
>>> t7.render(c)
u'[<Listing: RedirObject object listed in example.com/cat>, <Listing: RedirObject object listed in example.com/cat/subcat1>]'

manualy specified every contenttype, everything and objects.all are the same
----------------------------------------------------------------------------

>>> t8 = Template('{% listing 10 of redir_sample.redirobject, url_tests.samplemodel, url_tests.othersamplemodel as obj_list %}{{obj_list|safe}}')
>>> t8.render(c)
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>, <Listing: RedirObject object listed in example.com/cat/subcat1>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>]'

>>> t9 = Template('{% listing 10 as obj_list %}{{obj_list|safe}}')
>>> t9.render(c)
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat/subcat1>]'

>>> unicode(Listing.objects.all())
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/cat/subcat1>]'


"""
hits = r"""
>>> from django.template import Template, Context
>>> from ella.core.models import Placement, HitCount
>>> place =  Placement.objects.all()[0]

# test comment_count
>>> t = Template('{% load hits %}{% hitcount for place %}')
>>> t.render(Context({'place': place}))
u''
>>> HitCount.objects.get(pk=place.pk).hits
1

>>> t = Template('{%% load hits %%}{%% hitcount for pk %s %%}' % place.pk)
>>> t.render(Context({}))
u''
>>> HitCount.objects.get(pk=place.pk).hits
2

# hitcount with double_render
>>> from django.templatetags import hits
>>> hits.DOUBLE_RENDER = True

# test hitcount
>>> t = Template('{% load hits %}{% hitcount for place %}')
>>> t.render(Context({'place': place})) == u'{%% load hits %%}{%% hitcount for pk %d %%}' % place.pk
True
>>> t = Template(t.render(Context({'place': place})))
>>> t.render(Context({'SECOND_RENDER' : True}))
u''
>>> HitCount.objects.get(pk=place.pk).hits
3

>>> t = Template('{%% load hits %%}{%% hitcount for pk %s %%}' % place.pk)
>>> t.render(Context({})) == u'{%% load hits %%}{%% hitcount for pk %d %%}' % place.pk
True
>>> t = Template(t.render(Context({})))
>>> t.render(Context({'SECOND_RENDER' : True}))
u''
>>> HitCount.objects.get(pk=place.pk).hits
4

# hitcount with double_render
>>> hits.DOUBLE_RENDER = False


"""

__test__ = {
#    'listing' : listing,
    'hits' : hits
}


listing = r"""
>>> from ella.core.models import Listing, Category
>>> from django.template import Template, Context

>>> cat = Category.objects.get(pk=1)
>>> c = Context({'category': cat,})

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
u'[<Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com//cat>]'

manualy specified every contenttype, everything and objects.all are the same
----------------------------------------------------------------------------

>>> t4 = Template('{% listing 10 of redir_sample.redirobject, url_tests.samplemodel, url_tests.othersamplemodel as obj_list %}{{obj_list|safe}}')
>>> t4.render(c)
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com//cat>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>]'

>>> t5 = Template('{% listing 10 as obj_list %}{{obj_list|safe}}')
>>> t5.render(c)
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com//cat>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>]'

>>> unicode(Listing.objects.all())
u'[<Listing: SampleModel object listed in example.com/>, <Listing: RedirObject object listed in example.com/>, <Listing: RedirObject object listed in example.com//cat>, <Listing: SampleModel object listed in example.com/>, <Listing: OtherSampleModel object listed in example.com/>]'

"""


__test__ = {
    'listing' : listing,
}


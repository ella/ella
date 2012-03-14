from unittest import TestCase

from django.template import TemplateDoesNotExist

from nose import tools


templates = {}

def load_template_source(template_name, dirs=None):
    "Dummy template loader that returns templates from local templates dictionary."
    try:
        return templates[template_name], template_name
    except KeyError, e:
        raise TemplateDoesNotExist(e)
load_template_source.is_usable = True

class TestDummyTemplateLoader(TestCase):
    def tearDown(self):
        global templates
        templates = {}

    def test_simple(self):
        templates['anything.html'] = 'Something'
        source, name = load_template_source('anything.html')
        tools.assert_equals('anything.html', name)
        tools.assert_equals('Something', source)

    def test_empty(self):
        tools.assert_raises(TemplateDoesNotExist, load_template_source, 'anything.html')


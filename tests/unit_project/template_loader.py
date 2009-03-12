from djangosanetesting import UnitTestCase

from django.template import Template, TemplateDoesNotExist 


templates = {}

def load_template_source(template_name, dirs=None):
    "Dummy template loader that returns templates from local templates dictionary."
    try:
        return templates[template_name], template_name
    except KeyError, e:
        raise TemplateDoesNotExist(e)
load_template_source.is_usable = True

class TestDummyTemplateLoader(UnitTestCase):
    def tearDown(self):
        global templates
        templates = {}

    def test_simple(self):
        templates['anything.html'] = 'Something'
        source, name = load_template_source('anything.html')
        self.assert_equals('anything.html', name)
        self.assert_equals('Something', source)

    def test_empty(self):
        self.assert_raises(TemplateDoesNotExist, load_template_source, 'anything.html')


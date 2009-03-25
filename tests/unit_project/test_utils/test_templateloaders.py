from os.path import join, pardir, abspath, dirname

from djangosanetesting import UnitTestCase

from django.template import TemplateDoesNotExist

from ella.utils.template_loaders import _get_template_vars

class TestAppTemplateLoader(UnitTestCase):

    def test_returning_proper_name(self):
        self.assert_equals("template_name", _get_template_vars("core:template_name")[0])

    def test_returning_proper_dir(self):
        self.assert_equals(abspath(join(dirname(__file__), pardir, pardir, pardir, 'ella', 'core', 'templates')), _get_template_vars("core:template_name")[1])

    def test_invalid_name_raising_template_exc(self):
        self.assert_raises(TemplateDoesNotExist, _get_template_vars, \
            "total_invalid_application_do_not_use_or_i_will_kill_you:template_name")

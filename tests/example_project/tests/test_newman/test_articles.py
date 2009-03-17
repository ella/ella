
from example_project.tests.test_newman.helpers import NewmanTestCase

class TestArticleBasics(NewmanTestCase):

    # FIXME: remove
    def test_simple_login(self):
        self.login_superuser()
        self.logout()
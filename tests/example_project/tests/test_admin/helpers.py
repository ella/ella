from djangosanetesting import SeleniumTestCase

class AdminTestCase(SeleniumTestCase):
#    fixtures = ['fixture_with_admin_user']

    SUPERUSER_USERNAME = u"superman"
    SUPERUSER_PASSWORD = u"xxx"

    URI = "/admin/"

    def __init__(self):
        super(AdminTestCase, self).__init__()
        self.elements = {
            'navigation' : {
                'logout' : '//a[@href="%slogout/"]' % self.URI
            },
            'pages' : {
                'login' : {
                    'submit' : "//input[@type='submit']"
                }
            }
        }

    def login_superuser(self):
        self.selenium.open(self.URI)
        self.selenium.type("id_username", self.SUPERUSER_USERNAME)
        self.selenium.type("id_password", self.SUPERUSER_PASSWORD)
        self.selenium.click(self.elements['pages']['login']['submit'])

    def logout(self):
        self.selenium.click(self.elements['navigation']['logout'])
        self.selenium.wait_for_page_to_load(30000)


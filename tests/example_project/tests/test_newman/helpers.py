from djangosanetesting import SeleniumTestCase

class NewmanTestCase(SeleniumTestCase):
    fixtures = ['newman_admin_user', 'example_data']

    SUPERUSER_USERNAME = u"superman"
    SUPERUSER_PASSWORD = u"xxx"

    NEWMAN_URI = "/newman/"

    def __init__(self):
        super(NewmanTestCase, self).__init__()
        self.elements = {
            'navigation' : {
                'logout' : "//a[@class='icn logout']",
                'articles' : "//a[@class='app article']",
                'article_add' : "//a[@class='app article']/../a[position()=2]"
            },
            'pages' : {
                'login' : {
                    'submit' : "//input[@type='submit']"
                }
            }
        }

    def setUp(self):
        super(NewmanTestCase, self).setUp()
        self.login_superuser()

    def login_superuser(self):
        self.selenium.open(self.NEWMAN_URI)
        self.selenium.type("id_username", self.SUPERUSER_USERNAME)
        self.selenium.type("id_password", self.SUPERUSER_PASSWORD)
        self.selenium.click(self.elements['pages']['login']['submit'])

    def logout(self):
        self.selenium.click(self.elements['navigation']['logout'])
        self.selenium.wait_for_page_to_load(30000)
        self.selenium.is_text_present(u"Thanks for spending some quality time with the Web site today.")

    def tearDown(self):
        self.logout()
        super(NewmanTestCase, self).tearDown()

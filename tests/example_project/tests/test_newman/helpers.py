from djangosanetesting import SeleniumTestCase

class NewmanTestCase(SeleniumTestCase):
    fixtures = ['newman_admin_user', 'example_data']

    USER_USERNAME = u"superman"
    USER_PASSWORD = u"xxx"

    NEWMAN_URI = "/newman/"

    def __init__(self):
        super(NewmanTestCase, self).__init__()
        self.elements = {
            'navigation' : {
                'logout' : "//a[@class='icn logout']",
                'categories' : "//a[@class='app category']",
                'categories_add' : "//a[@class='app category']/../a[position()=2]",
                'articles' : "//a[@class='app article']",
                'article_add' : "//a[@class='app article']/../a[position()=2]",
            },
            'controls' : {
                'suggester' : "//div[@class='suggest-bubble']",
                'suggester_visible' : "//span[@class='hilite']",
                'message' : {
                    'ok': "//div[@id='opmsg']/span[@class='okmsg']",
                },
                'add' : "//a[@class='hashadr icn btn add']",
                'save' : "//a[@class='submit icn btn save def']",
                'show_filters' : "//div[@id='filters-handler']/a",
            },
            'pages' : {
                'login' : {
                    'submit' : "//input[@type='submit']"
                },
                'listing' : {
                    'first_object' : "//div[@id='changelist']/form/table/tbody/tr[@class='row1']",
                    'object' : "//div[@id='changelist']/form/table/tbody/tr[@class='row%(position)s']",
                }
            }
        }

    def setUp(self):
        super(NewmanTestCase, self).setUp()
        self.login()

    def login(self):
        self.selenium.open(self.NEWMAN_URI)
        self.selenium.type("id_username", self.USER_USERNAME)
        self.selenium.type("id_password", self.USER_PASSWORD)
        self.selenium.click(self.elements['pages']['login']['submit'])

    def logout(self):
        self.selenium.click(self.elements['navigation']['logout'])
        self.selenium.wait_for_page_to_load(30000)
        self.selenium.is_text_present(u"Thanks for spending some quality time with the Web site today.")

    def tearDown(self):
        self.logout()
        super(NewmanTestCase, self).tearDown()


    def get_listing_object(self, position=1):
        return self.elements['pages']['listing']['object'] % {
            'position' : position
        }

    def fill_fields(self, data):
        s = self.selenium
        for key, value in data.items():
            s.type(key, value)

    def fill_suggest_fields(self, suggest_data):
        s = self.selenium
        for key, values in suggest_data.items():
            for value in values:
                id = 'id_%s_suggest' % key
                s.click(id)
                s.type(id, value)
                s.click(id)
                s.wait_for_element_present(self.elements['controls']['suggester_visible'])
                s.click(self.elements['controls']['suggester_visible'])

    def fill_calendar_fields(self, calendar_data):
        """
        Select date from calendars. Calendar_data is dict in form of {
            "field" : {
                "day" : int,
            }
        }, where day of the current month is selected.
        (support for other fields is TODO)
        """
        s = self.selenium
        for field in calendar_data:
            # click on calendar button
            xpath = "//td[@class='%(field)s']/span[@class='datepicker-trigger']" % {
                "field" : field
            }
            s.click(xpath)

            # chose the current date
            xpath = "//table[@class='ui-datepicker-calendar']/tbody/tr/td/a[text()='%(day)s']" % {
                "day" : calendar_data[field]['day']
            }
            s.click(xpath)


    def save_form(self):
        s = self.selenium
        s.click(self.elements['controls']['save'])
        s.wait_for_element_present(self.elements['controls']['message']['ok'])


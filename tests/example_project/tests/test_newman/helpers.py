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
                'suggester_selected' : "//input[@id='id_%(field)s']/../ul/li[@class='suggest-selected-item']",
                'message' : {
                    'ok': "//div[@id='opmsg']/span[@class='okmsg']",
                },
                'add' : "//a[@class='hashadr icn btn add']",
                'save' : "//a[@class='submit icn btn save def']",
                'show_filters' : "//div[@id='filters-handler']/a",
                'lookup_content' : "//div[@id='changelist']/form/table/tbody/tr/th/a[text()='%(text)s']",
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


    def fill_using_lookup(self, data):
        """
        Fill data using "magnifier".
        @param data is dictionary of fields and values, in form:
        {
            "field" : "value",
        }
        where field is name of field magnifier is bound to and value is a content of the element from the list
        """
        s = self.selenium
        for field in data:
            xpath = "lookup_id_%s" % field
            s.click(xpath)
            s.click(self.elements['controls']['lookup_content'] % {'text' : data[field]})

    def save_form(self):
        s = self.selenium
        s.click(self.elements['controls']['save'])
        s.wait_for_element_present(self.elements['controls']['message']['ok'])

    def get_formatted_form_errors(self, errors):
        messages = []
        for field in errors:
            expected = errors[field]['expected']
            retrieved = errors[field]['retrieved']

            if isinstance(expected, list):
                expected = u"".join(expected).encode('utf-8')

            if isinstance(retrieved, list):
                retrieved = u"".join(retrieved).encode('utf-8')

            messages.append("Form validation for field %(field)s was expecting %(expected)s, but got %(retrieved)s" % {
                'field' : field,
                'expected' : expected,
                'retrieved' : retrieved,
            })
            
        return '\n'.join(messages)

    def verify_form(self, data):
        errors = {}
        for field in data:
            if isinstance(data[field], list):
                for i in xrange(0, len(data[field])):
                    xpath = (self.elements['controls']['suggester_selected']+"[%(number)s]") % {
                        'field' : field,
                        'number' : i+1, # xpath indexes from 1 :]
                    }
                    text = self.selenium.get_text(xpath)
                    if text != data[field][i]:
                        errors[field] = {
                            'expected' : data[field],
                            'retrieved' : text,
                        }
            else:
                text = self.selenium.get_value('id_%s' % field)
                if text != data[field]:
                    errors[field] = {
                        'expected' : data[field],
                        'retrieved' : text,
                    }

        if len(errors) > 0:
            raise AssertionError(self.get_formatted_form_errors(errors))


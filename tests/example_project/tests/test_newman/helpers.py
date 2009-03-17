from djangosanetesting import SeleniumTestCase

class NewmanTestCase(SeleniumTestCase):
    fixtures = ['newman_admin_user']

    SUPERUSER_USERNAME = u"superman"
    SUPERUSER_PASSWORD = u"xxx"

    NEWMAN_URI = "/newman/"

    def login_superuser(self):
        self.selenium.open(self.NEWMAN_URI)
        self.selenium.type("id_username", self.SUPERUSER_USERNAME)
        self.selenium.type("id_password", self.SUPERUSER_PASSWORD)
        self.selenium.click("//input[@type='submit']")

    def logout(self):
        self.selenium.click('//a[@href="%slogout/"]' % self.NEWMAN_URI)
        self.selenium.is_text_present(u"Thanks for spending some quality time with the Web site today.")


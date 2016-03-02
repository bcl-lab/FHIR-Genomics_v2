from BeautifulSoup import BeautifulSoup
from seleniumbase import BaseCase

class MyTestClass(BaseCase):

    localhost_email = "name@mail.com"
    localhost_password = "password"

    def test_basic(self):
        self.open("http://localhost:8000/resources/Patient")
        self.update_text("#inputEmail", self.localhost_email)
        self.update_text("#inputPassword", self.localhost_password)
        self.click('button[type="Submit"]')
        self.wait_for_text_visible("reportforgenetics", "body")
        self.wait_for_text_visible("Condition", "body")
        self.click('button[name="authorize"]')
        self.wait_for_text_visible("Patient", "table")
        base_url = self.driver.current_url.split('/r')[0]
        source = self.driver.page_source
        soup = BeautifulSoup(source)
        num_rows = len(soup.fetch("a")) - 3  # Skip header, etc
        for i in xrange(num_rows):
            href = soup.fetch("a")[i+3].attrs[0][1]
            self.open(base_url + href)
            self.wait_for_text_visible("Genetics Report for", "h3")
            self.wait_for_text_visible("Clinical Context", "h4")
            self.wait_for_text_visible("Genetics Information", "body")

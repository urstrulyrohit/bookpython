from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from book import Book


class Bibli:
    def __init__(self, card_number, password):
        self.driver = webdriver.Chrome()
        self.driver.get("http://sagu.ent.sirsidynix.net/client/fr_FR/formation")
        self.book_objects = []
        self.card_number = card_number
        self.password = password
        self.login()

    def login(self):
        if self.is_logged_in():
            return

        print('Logging in...')
        elem = self.driver.find_element_by_css_selector('.menuLink > a[tabindex="2"]')
        elem.click()
        login_iframe = WebDriverWait(self.driver, 10)\
            .until(lambda driver: driver.find_element_by_css_selector('#loginModal > iframe'))
        self.driver.switch_to.frame(login_iframe)
        username = self.driver.find_element_by_id('j_username')
        username.clear()
        username.send_keys(self.card_number)
        password = self.driver.find_element_by_id('j_password')
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 20).until(lambda driver: driver.find_element_by_id('checkoutsSummary'))
        print('Logged in!!')

    def is_logged_in(self):
        try:
            self.driver.find_element_by_css_selector('#libInfoContainer > .welcome')
            return True
        except NoSuchElementException:
            return False

    def hydrate_books(self):
        self.login()
        print('Waiting for books to be fetched...')
        locator = self.driver.find_element_by_css_selector('.myAccountLoadingHolder')
        WebDriverWait(self.driver, 10).until(expected_conditions.invisibility_of_element_located(locator))
        dom_books = self.driver.find_elements_by_css_selector('.checkoutsLine')

        # TODO: Find element with corresponding index (0, 1, 2, etc) as ID detailZone[INDEX] (ex. detailZone0)
        # ^(need to click it first and wait..!)
        # TITLE IS #detail_biblio0 .INITIAL_TITLE_SRCH
        # AUTHOR IS #detail_biblio0 .PERSONAL_AUTHOR
        # PAGES AND SIZE IS #detail_biblio0 .PHYSICAL_DESC (needs to be parsed)

        for dom_book in dom_books:
            book_object = Book()
            book_object.author = dom_book.find_element_by_class_name('checkouts_author').text

            book_object.due_date = dom_book.find_element_by_class_name('checkoutsDueDate').text
            book_object.renewed = int(dom_book.find_element_by_class_name('checkoutsRenewCount').text)
            book_object.id = dom_book.find_element_by_class_name('checkouts_itemId').text
            book_object.title = dom_book.find_element_by_class_name('hideIE').text
            self.book_objects.append(book_object)
        print('Books hydrated!')

    def close(self):
        self.driver.close()

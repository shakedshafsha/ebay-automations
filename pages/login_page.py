import re
from playwright.sync_api import Page, expect

from config.urls import EBAY_SIGNIN_PAGE
from .base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.sign_in_link = page.get_by_role("link", name=re.compile("sign in", re.I))
        self.email_input = page.locator("#userid")
        self.continue_btn = page.locator("#signin-continue-btn")
        self.password_input = page.locator("#pass")
        self.signin_btn = page.locator("#sgnBt")
        self.account_indicator = page.get_by_text(re.compile("my ebay", re.I))

    def go_to_login(self):
        if self.sign_in_link.is_visible():
            self.sign_in_link.click()
        else:
            self.page.goto(EBAY_SIGNIN_PAGE)

        expect(self.email_input).to_be_visible()

    def login(self, username: str, password: str):
        self.go_to_login()

        self.email_input.fill(username)
        self.continue_btn.click()

        expect(self.password_input).to_be_visible()

        self.password_input.fill(password)
        self.signin_btn.click()

        self._wait_for_login_success()

    def is_logged_in(self) -> bool:
        try:
            return self.account_indicator.is_visible()
        except:
            return False

    def ensure_logged_in(self, username: str, password: str):
        if self.is_logged_in():
            return

        self.login(username, password)

    def _wait_for_login_success(self):
        try:
            expect(self.account_indicator).to_be_visible()
        except Exception:
            self.page.wait_for_load_state("networkidle")
# pages/item_page.py
import re
import random
from typing import List
from playwright.sync_api import Page, expect


class ItemPage:
    def __init__(self, page: Page):
        self.page = page

        self.price = page.locator(".x-price-primary span")
        self.add_to_cart_btn = page.get_by_role("button", name=re.compile("add to cart", re.I))
        self.buy_now_btn = page.get_by_role("button", name=re.compile("buy", re.I))
        self.variation_selects = page.locator("select")

    def add_items_to_cart(self, urls: List[str]) -> None:

        for i, url in enumerate(urls):
            self.page.goto(url)

            expect(self.price).to_be_visible()

            self._select_random_variations()

            if self.add_to_cart_btn.is_visible():
                self.add_to_cart_btn.click()
            elif self.buy_now_btn.is_visible():
                self.buy_now_btn.click()
            else:
                continue

            self.page.wait_for_load_state("domcontentloaded")
            self.page.screenshot(path=f"screenshots/item_{i}.png")
            self.page.go_back()
            self.page.wait_for_load_state("domcontentloaded")

    def select_random_variations(self):
        if self.variation_selects.count() == 0:
            return

        for i in range(self.variation_selects.count()):
            dropdown = self.variation_selects.nth(i)
            options = dropdown.locator("option")

            if options.count() > 1:
                index = random.randint(1, options.count() - 1)
                dropdown.select_option(index=index)
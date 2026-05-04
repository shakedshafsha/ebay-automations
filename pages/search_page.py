# pages/search_page.py
import re
from typing import List
from playwright.sync_api import Page, expect

from config.urls import EBAY_HOME_PAGE
from utils.helpers import extract_price

class SearchPage:
    def __init__(self, page: Page):
        self.page = page

        self.search_box = page.get_by_role("combobox", name="Search for anything")
        self.search_button = page.get_by_role("button", name="Search", exact=True)

        self.max_price_input = page.get_by_role("textbox", name=re.compile("max", re.I))

        self.items = page.locator("li.s-item")
        self.next_button = page.get_by_role("link", name=re.compile("next", re.I))

    def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> List[str]:

        self.open_home_page()
        self.search(query)
        self.apply_max_price_filter(max_price)

        return self.collect_items_with_paging(max_price, limit)

    def open_home_page(self):
        self.page.goto(EBAY_HOME_PAGE)

    def search(self, query: str):
        self.search_box.fill(query) 
        self.search_box.press("Enter")
        expect(self.items.first).to_be_visible

    def apply_max_price_filter(self, max_price: float):
        try:
            self.max_price_input.fill(str(max_price))
            self.max_price_input.press("Enter")
        except Exception:
            pass

    def collect_items_with_paging(
        self, max_price: float, limit: int
    ) -> List[str]:

        results = []

        while len(results) < limit:
            results.extend(self.collect_items_from_current_page(max_price, limit - len(results)))

            if len(results) >= limit:
                break

            if not self.go_to_next_page():
                break

        return results

    def collect_items_from_current_page(
        self, max_price: float, remaining: int
    ) -> List[str]:

        collected = []

        count = self.items.count()

        for i in range(count):
            if len(collected) >= remaining:
                break

            item = self.items.nth(i)

            if not self.has_price(item):
                continue

            price = self.get_item_price(item)

            if price > max_price:
                continue

            link = self.get_item_link(item)

            if link:
                collected.append(link)

        return collected

    def has_price(self, item) -> bool:
        return item.locator(".s-item__price").count() > 0

    def get_item_price(self, item) -> float:
        text = item.locator(".s-item__price").inner_text()
        return extract_price(text)

    def get_item_link(self, item) -> str:
        link = item.locator("a.s-item__link").get_attribute("href")
        return link if link and "itm" in link else None

    def go_to_next_page(self) -> bool:
        try:
            if self.next_button.is_visible():
                self.next_button.click()
                self.page.wait_for_load_state("domcontentloaded")
                return True
            return False
        except Exception:
            return False

   
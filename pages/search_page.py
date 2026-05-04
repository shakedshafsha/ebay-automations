# pages/search_page.py
import re
from typing import List
from playwright.sync_api import Page, expect

from utils.helpers import extract_price

class SearchPage:
    def __init__(self, page: Page):
        self.page = page

        self.search_box = page.get_by_role("combobox", name="Search for anything")
        self.search_button = page.get_by_role("button", name="Search")

        self.max_price_input = page.get_by_role("textbox", name=re.compile("max", re.I))

        self.items = page.locator("li.s-item")
        self.next_button = page.get_by_role("link", name=re.compile("next", re.I))

    def searchItemsByNameUnderPrice(
        self, query: str, max_price: float, limit: int = 5
    ) -> List[str]:

        self._open_homepage()
        self._search(query)
        self._apply_max_price_filter(max_price)

        return self._collect_items_with_paging(max_price, limit)

    def open_homepage(self):
        self.page.goto("https://www.ebay.com")

    def search(self, query: str):
        self.search_box.fill(query)
        self.search_button.click()
        expect(self.items.first).to_be_visible()

    def apply_max_price_filter(self, max_price: float):
        try:
            self.max_price_input.fill(str(max_price))
            self.max_price_input.press("Enter")
            self.page.wait_for_load_state("networkidle")
        except Exception:
            # fallback – ignore if not available
            pass

    def collect_items_with_paging(
        self, max_price: float, limit: int
    ) -> List[str]:

        results = []

        while len(results) < limit:
            results.extend(self._collect_items_from_current_page(max_price, limit - len(results)))

            if len(results) >= limit:
                break

            if not self._go_to_next_page():
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

            if not self._has_price(item):
                continue

            price = self._get_item_price(item)

            if price > max_price:
                continue

            link = self._get_item_link(item)

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

   
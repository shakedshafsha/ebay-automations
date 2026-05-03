import re
from playwright.sync_api import Page

class SearchPage:
    def __init__(self, page: Page):
        self.page = page
        # Selectors
        self.SEARCH_BOX = "#gh-ac"
        self.SEARCH_BTN = self.page.get_by_role("button", name="Search")
        self.ITEMS_CONTAINER = "ul.srp-results .s-item"
        self.ITEM_LINK = "a.s-item__link"
        self.ITEM_PRICE = "span.s-item__price"
        self.NEXT_PAGE_BTN = "a.pagination__next"

    def navigate(self):
        self.page.goto("https://www.ebay.com")

    def apply_price_filter(self, min_price: float, max_price: float):
        
        min_input = self.page.locator("//input[contains(@aria-label,'Min')]")
        max_input = self.page.locator("//input[contains(@aria-label,'Max')]")

        min_input.fill(str(min_price))
        max_input.fill(str(max_price))

        max_input.press("Enter")

    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5):
        
        self.navigate()

        self.page.fill(self.SEARCH_BOX, query)
        self.SEARCH_BTN.click()
        
        try:
            self.apply_price_filter(0,max_price)
        except Exception:
            print("Price filter not available, filtering manually.")

        results_urls = []

        while len(results_urls) < limit:

            self.page.locator("li.s-item").first.wait_for()

            items = self.page.locator("li.s-item")

            for item in items.all():
                if len(results_urls) >= limit:
                    break

                price_text = item.locator("span.s-item__price").inner_text()
                price_value = self._extract_price(price_text)

                if price_value <= max_price:
                    url = item.locator("a.s-item__link").get_attribute("href")

                    if url and "itm" in url:
                        results_urls.append(url)

            next_btn = self.page.locator("a.pagination__next")

            if next_btn.is_visible():
                next_btn.click()
                self.page.wait_for_load_state("domcontentloaded")
            else:
                break

        return results_urls

    def _extract_price(self, price_str: str) -> float:
        try:
            first_price = price_str.split("to")[0]
            clean_price = re.sub(r'[^\d.]', '', first_price)
            return float(clean_price)
        except:
            return float('inf') 
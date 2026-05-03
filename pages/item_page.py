from .base_page import BasePage
import re


class ItemPage(BasePage):

    def _parse_price(self, text):
        match = re.search(r"(\d+[.,]?\d*)", text.replace(",", ""))
        return float(match.group(1)) if match else None

    def add_to_cart(self, url, index: int):
        self.page.goto(url)

        price_text = self.page.locator(".x-price-primary span").inner_text()
        price = self._parse_price(price_text)   

        self.page.get_by_role("button", name="Add to cart").click()

        self.take_screenshot(f"item_{index}")

        return price
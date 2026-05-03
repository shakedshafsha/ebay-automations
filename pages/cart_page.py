from .base_page import BasePage
import re

class CartPage(BasePage):

    def get_total(self):
        self.page.goto("https://cart.ebay.com")

        total_text = self.page.locator(".cart-bucket-lineitem-total").inner_text()

        match = re.search(r"(\d+[.,]?\d*)", total_text.replace(",", ""))
        return float(match.group(1)) if match else None

    def assert_total_not_exceeds(self, budget_per_item: float, items_count: int):
        total = self.get_total()
        assert total is not None

        max_allowed = budget_per_item * items_count

        assert total <= max_allowed, f"Cart total {total} exceeds {max_allowed}"

        self.take_screenshot("cart")
import re
from playwright.sync_api import Page

from config.urls import EBAY_CART_PAGE

class CartPage:
    def __init__(self, page: Page):
        self.page = page

        self.total = page.locator(".cart-bucket-lineitem-total")

    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int):

        self.page.goto(EBAY_CART_PAGE)

        total_text = self.total.inner_text()

        match = re.search(r"(\d+[.,]?\d*)", total_text.replace(",", ""))
        total = float(match.group(1)) if match else 0

        max_allowed = budget_per_item * items_count

        assert total <= max_allowed, f"{total} > {max_allowed}"

        self.page.screenshot(path="screenshots/cart.png")
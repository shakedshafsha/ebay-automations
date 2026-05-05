import os
from typing import List
from playwright.sync_api import Page

from config.urls import EBAY_CART_PAGE


class CartPage:
    def __init__(self, page: Page):
        self.page = page

    def clear_cart(self) -> None:
        self.page.goto(EBAY_CART_PAGE)
        self.page.wait_for_load_state("domcontentloaded")

        for _ in range(30):
            clicked = self.page.evaluate("""
                () => {
                    const el = [...document.querySelectorAll('button, a, [role="button"]')]
                        .find(e => /^remove$/i.test((e.innerText || e.textContent || '').trim()));
                    if (el) { el.click(); return true; }
                    return false;
                }
            """)
            if not clicked:
                print("[CART] Cart is empty or Remove button not found — stopping clear.")
                break
            self.page.wait_for_load_state("domcontentloaded")

    def assert_cart_total_not_exceeds(self, budget_per_item: float, actual_prices: List[float]) -> None:
        max_allowed = round(budget_per_item * len(actual_prices), 2)
        actual = round(sum(actual_prices), 2)

        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/cart.png")

        print(f"\n[ASSERT] Cart subtotal : {actual}")
        print(f"[ASSERT] Max allowed   : {max_allowed}  ({budget_per_item} × {len(actual_prices)} items)")

        assert actual <= max_allowed, (
            f"Cart subtotal ({actual}) exceeds max allowed ({max_allowed})"
        )
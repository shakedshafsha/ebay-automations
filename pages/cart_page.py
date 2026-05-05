import os
import re
from typing import List
from playwright.sync_api import Page

from config.urls import EBAY_CART_PAGE
from utils.helpers import extract_price


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

    def _read_cart_subtotal(self) -> float:
        self.page.goto(EBAY_CART_PAGE)
        self.page.wait_for_load_state("networkidle")

        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/cart_debug.png", full_page=True)

        debug_info = self.page.evaluate("""
            () => {
                const priceRe = /^(?:US\\s*)?\\$?\\s*([\\d,]+\\.\\d{2})$/;
                return [...document.querySelectorAll('*')]
                    .filter(el => el.children.length === 0)
                    .map(el => ({
                        text: (el.textContent || '').trim(),
                        tag:  el.tagName,
                        cls:  (el.className || '').substring(0, 80)
                    }))
                    .filter(({text}) => priceRe.test(text));
            }
        """)
        print(f"\n[CART DEBUG] {len(debug_info)} price element(s) found on cart.ebay.com:")
        for el in debug_info:
            print(f"  [{el['tag']}] cls='{el['cls']}' → '{el['text']}'")

        subtotal = self.page.evaluate("""
            () => {
                const priceRe = /([\\d,]+\\.\\d{2})/;
                const subtotalLabel = [...document.querySelectorAll('*')]
                    .find(el =>
                        el.children.length === 0 &&
                        /subtotal/i.test((el.textContent || '').trim())
                    );

                if (!subtotalLabel) return null;
                for (let node = subtotalLabel.parentElement; node && node.tagName !== 'BODY'; node = node.parentElement) {
                    const siblings = node.parentElement
                        ? [...node.parentElement.children].filter(s => s !== node)
                        : [];
                    for (const sib of siblings) {
                        const m = (sib.textContent || '').match(priceRe);
                        if (m) return m[0];
                    }
                }
                return null;
            }
        """)

        if subtotal:
            value = extract_price(subtotal)
            print(f"[CART] Subtotal read from page: {value}")
            return value

        raise RuntimeError(
            "Could not find cart subtotal.\n"
            "→ Open screenshots/cart_debug.png and look at the [CART DEBUG] lines above.\n"
            "→ Find which element/class holds the subtotal and add it to _read_cart_subtotal()."
        )

    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int) -> None:
        max_allowed = round(budget_per_item * items_count, 2)
        actual = self._read_cart_subtotal()

        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/cart.png")

        print(f"\n[ASSERT] Cart subtotal : {actual}")
        print(f"[ASSERT] Max allowed   : {max_allowed}  ({budget_per_item} * {items_count})")

        assert actual <= max_allowed, (
            f"Cart subtotal ({actual}) exceeds max allowed ({max_allowed})"
        )
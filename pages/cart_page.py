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

    def _read_cart_total(self) -> float:
        self.page.goto(EBAY_CART_PAGE)
        self.page.wait_for_load_state("domcontentloaded")

        try:
            self.page.wait_for_selector("text=/US \\$/", timeout=15000)
        except Exception:
            pass

        total = self.page.evaluate("""
            () => {
                const numRe   = /([\\d,]+\\.\\d{2})/;
                const priceRe = /^US\\s*\\$\\s*[\\d,]+\\.\\d{2}$/;

                const label = [...document.querySelectorAll('*')].find(el =>
                    el.children.length === 0 &&
                    /^(subtotal|order total|items total):?$/i.test((el.textContent || '').trim())
                );
                if (label) {
                    for (let node = label.parentElement; node && node.tagName !== 'BODY'; node = node.parentElement) {
                        for (const sib of [...(node.parentElement?.children ?? [])].filter(s => s !== node)) {
                            const m = (sib.textContent || '').match(numRe);
                            if (m) return parseFloat(m[0].replace(/,/g, ''));
                        }
                    }
                }
                const all       = [...document.querySelectorAll('*')];
                const priceEls  = all.filter(el => priceRe.test((el.textContent || '').trim()));
                const innermost = priceEls.filter(el =>
                    !priceEls.some(other => other !== el && el.contains(other))
                );
                return parseFloat(
                    innermost
                        .map(el => parseFloat(((el.textContent || '').match(numRe) || ['0'])[0].replace(/,/g, '')))
                        .reduce((a, b) => a + b, 0)
                        .toFixed(2)
                );
            }
        """)

        value = float(total)
        print(f"[CART] Total read from cart page: {value}")
        return value

    def assert_cart_total_not_exceeds(self, budget_per_item: float, actual_prices: List[float]) -> None:
        max_allowed = round(budget_per_item * len(actual_prices), 2)
        cart_total  = self._read_cart_total()

        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/cart.png")

        print(f"\n[ASSERT] Cart total (eBay page)           : {cart_total}")
        print(f"[ASSERT] Budget threshold ({budget_per_item} × {len(actual_prices)}) : {max_allowed}")

        assert cart_total <= max_allowed, (
            f"Cart total ({cart_total}) exceeds budget threshold ({max_allowed})"
        )

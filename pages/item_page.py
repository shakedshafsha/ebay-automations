import os
import re
import random
from typing import List
from playwright.sync_api import Page, expect

from utils.helpers import extract_price


class ItemPage:
    def __init__(self, page: Page):
        self.page = page
        self.price         = page.locator(".x-price-primary span.ux-textspans").first
        self.add_to_cart_btn = page.get_by_role("button", name=re.compile("add to cart", re.I))
        self.buy_now_btn   = page.get_by_role("button", name=re.compile("buy", re.I))

    def add_items_to_cart(self, urls: List[str]) -> List[float]:
        collected_prices: List[float] = []
        os.makedirs("screenshots", exist_ok=True)

        for url in urls:
            self.page.goto(url, wait_until="domcontentloaded")
            expect(self.price).to_be_visible()
            self.select_random_variations()
            item_price = extract_price(self.price.inner_text())

            if self.add_to_cart_btn.is_visible():
                self.add_to_cart_btn.click()
            elif self.buy_now_btn.is_visible():
                self.buy_now_btn.click()
            else:
                print(f"[SKIP] No add-to-cart or buy button found on {url}")
                continue

            self.page.wait_for_load_state("domcontentloaded")
            collected_prices.append(item_price)

            idx = len(collected_prices)
            screenshot_path = f"screenshots/item_{idx}.png"
            self.page.screenshot(path=screenshot_path)
            print(f"[OK] Added item {idx} — price: {item_price} | screenshot: {screenshot_path}")

        return collected_prices

    def select_random_variations(self) -> None:
        self._select_dropdown_variations()
        self._select_button_group_variations()

    def _select_dropdown_variations(self) -> None:
        selects = self.page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            try:
                if not sel.is_visible():
                    continue
                options = sel.locator("option")
                valid = [
                    options.nth(j).get_attribute("value")
                    for j in range(options.count())
                    if options.nth(j).get_attribute("value") and not options.nth(j).is_disabled()
                ]
                if not valid:
                    continue
                chosen = random.choice(valid)
                sel.select_option(value=chosen)
                print(f"[VAR] dropdown #{i} → '{chosen}'")
            except Exception as e:
                print(f"[WARN] dropdown #{i} failed: {e}")

    def _select_button_group_variations(self) -> None:
        for selector in [
            "[data-testid='x-msku-selection-node']",
            "[data-testid='ux-selector-section']",
            ".x-msku__select-box",
        ]:
            groups = self.page.locator(selector)
            if groups.count() == 0:
                continue
            for i in range(groups.count()):
                options = groups.nth(i).locator(
                    "button:not([disabled]):not([aria-disabled='true']), "
                    "[role='option']:not([aria-disabled='true'])"
                )
                if options.count() == 0:
                    continue
                try:
                    choice = options.nth(random.randint(0, options.count() - 1))
                    choice.scroll_into_view_if_needed()
                    choice.click()
                    print(f"[VAR] button group '{selector}' #{i} → clicked")
                except Exception as e:
                    print(f"[WARN] button group '{selector}' #{i} failed: {e}")
            break

import re
import random
from typing import List
from playwright.sync_api import Page, expect

from utils.helpers import extract_price


class ItemPage:
    def __init__(self, page: Page):
        self.page = page
        self.price = page.locator(".x-price-primary span.ux-textspans").first
        self.add_to_cart_btn = page.get_by_role("button", name=re.compile("add to cart", re.I))
        self.buy_now_btn = page.get_by_role("button", name=re.compile("buy", re.I))

    def add_items_to_cart(self, urls: List[str]) -> List[float]:
        collected_prices: List[float] = []

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
                print(f"[SKIP] No add-to-cart or buy button visible on {url}")
                continue

            self.page.wait_for_load_state("domcontentloaded")
            collected_prices.append(item_price)
            print(f"[OK] Added item — price: {item_price}")

        return collected_prices

    def select_random_variations(self):
        all_selects = self.page.locator("select:visible, select")
        for i in range(all_selects.count()):
            sel = all_selects.nth(i)
            try:
                if not sel.is_visible():
                    continue
                options = sel.locator("option")
                valid_values = [
                    options.nth(j).get_attribute("value")
                    for j in range(options.count())
                    if options.nth(j).get_attribute("value")
                    and not options.nth(j).is_disabled()
                ]
                if not valid_values:
                    continue
                chosen = random.choice(valid_values)
                sel.select_option(value=chosen)
                print(f"[VAR] <select> #{i} → chose '{chosen}'")
            except Exception as e:
                print(f"[WARN] <select> #{i} failed: {e}")

        group_selectors = [
            "[data-testid='x-msku-selection-node']",
            "[data-testid='ux-selector-section']",
            ".x-msku__select-box",
        ]
        for group_sel in group_selectors:
            groups = self.page.locator(group_sel)
            count = groups.count()
            if count == 0:
                continue
            print(f"[VAR] Found {count} button group(s) via '{group_sel}'")
            for i in range(count):
                group = groups.nth(i)
                options = group.locator(
                    "button:not([disabled]):not([aria-disabled='true']), "
                    "[role='option']:not([aria-disabled='true'])"
                )
                n = options.count()
                if n == 0:
                    continue
                option = options.nth(random.randint(0, n - 1))
                try:
                    option.scroll_into_view_if_needed()
                    option.click()
                    print(f"[VAR] Button group '{group_sel}' #{i} → clicked option #{i}")
                except Exception as e:
                    print(f"[WARN] Button group '{group_sel}' #{i} failed: {e}")
            break 
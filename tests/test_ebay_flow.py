import json
from pages.search_page import SearchPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage


def test_ebay_e2e_flow(page):
    with open("data/test_data.json") as f:
        data = json.load(f)

    search_page = SearchPage(page)
    item_page = ItemPage(page)
    cart_page = CartPage(page)

    items = search_page.search_items_by_name_under_price(
        data["search_query"],
        data["max_price"],
        data["items_limit"]
    )

    prices = []

    for i, url in enumerate(items):
        price = item_page.add_to_cart(url, i)
        if price:
            prices.append(price)

    cart_page.assert_total_not_exceeds(
        data["max_price"],
        len(prices)
    )
import pytest
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
from utils.helpers import load_test_data


class TestEbayE2E:

    @pytest.mark.parametrize("test_case", load_test_data())
    def test_ebay_purchase_flow(self, page, test_case):

        login_page = LoginPage(page)
        search_page = SearchPage(page)
        item_page = ItemPage(page)
        cart_page = CartPage(page)

        # login_page.ensure_logged_in(
        #     username=test_case["user_name"],
        #     password=test_case["password"]
        # )

        urls = search_page.search_items_by_name_under_price(
            query=test_case["search_query"],
            max_price=test_case["max_price"],
            limit=test_case["items_limit"]
        )

        assert urls, (
            f"Aucun item trouvé pour '{test_case['search_query']}' "
            f"sous {test_case['max_price']} — vérifie les sélecteurs ou le réseau."
        )

        cart_page.clear_cart()

        prices = item_page.add_items_to_cart(urls)

        cart_page.assert_cart_total_not_exceeds(
            budget_per_item=test_case["max_price"],
            actual_prices=prices
        )
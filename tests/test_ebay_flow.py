import pytest
import json
from pages.search_page import SearchPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
from utils.helpers import load_test_data

# פונקציית עזר לטעינת הנתונים מהקובץ החיצוני

class TestEbayE2E:
    
    @pytest.mark.parametrize("test_case", load_test_data()) 
    def test_ebay_purchase_flow(self, page, test_case):
        search_page = SearchPage(page)
        item_page = ItemPage(page)
        cart_page = CartPage(page)

        urls = search_page.search_items_by_name_under_price(
            query=test_case["search_query"],
            max_price=test_case["max_price"],
            limit=test_case["items_limit"]
        )       
  
        if not urls:
            pytest.skip(f"No items found for {test_case['search_query']} under {test_case['max_price']}")

        item_page.add_items_to_cart(urls)

        cart_page.assert_cart_total_not_exceeds(
            budget_per_item=test_case["max_price"],
            items_count=len(urls)
        )
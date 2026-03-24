#############################################################################
# modules_test.py
#
# Final Unit 3 version. Uses Mocking to satisfy assignment requirements
# and handles the "id" vs "product_id" mapping.
#############################################################################

import math
import sys
import os
import unittest
from unittest.mock import patch

# Ensures the runner can find modules.py in the current directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import modules
from modules import (
    load_products,
    get_product_by_id,
    init_cart,
    add_to_cart,
    remove_from_cart,
    update_qty,
    calc_total,
    checkout_message,
    display_genai_advice
)

# =============================================================================
# TESTS
# =============================================================================

class TestModules(unittest.TestCase):

    @patch('modules.data_fetcher.get_products')
    def test_load_products_is_valid(self, mock_get_products):
        """Tests that load_products fetches and formats database data."""
        # We tell the mock to return data with the 'product_id' key (DB style)
        mock_get_products.return_value = [
            {"product_id": "h001", "name": "Howard Cap", "price": 25.00}
        ]
        
        products = load_products()
        
        # Verify the list isn't empty and keys were mapped to 'id' (UI style)
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["id"], "h001") 

    @patch('modules.data_fetcher.get_products')
    def test_get_product_by_id_found(self, mock_get_products):
        """Tests finding a product in the list by its ID."""
        mock_get_products.return_value = [
            {"product_id": "h001", "name": "Howard Cap"}
        ]
        
        products = load_products()
        target_id = products[0]["id"]
        
        found = get_product_by_id(products, target_id)
        self.assertIsNotNone(found)
        self.assertEqual(found["id"], "h001")

    @patch('modules.data_fetcher.get_products')
    def test_calc_total_basic(self, mock_get_products):
        """Tests total calculation for items in the cart."""
        mock_get_products.return_value = [
            {"product_id": "h001", "price": 25.00}
        ]
        
        products = load_products()
        cart = {"h001": 2} # 2 hats at $25.00
        total = calc_total(cart, products)
        
        self.assertTrue(math.isclose(total, 50.00, rel_tol=1e-9))

    def test_add_to_cart_new_item(self):
        """Tests adding a new item to an empty cart."""
        cart = init_cart()
        add_to_cart(cart, "h001", qty=1)
        self.assertEqual(cart, {"h001": 1})

    def test_checkout_message(self):
        """Tests the string formatting of the checkout success message."""
        fake_cart = {"h001": 2}
        fake_products = [{"id": "h001", "name": "Howard Cap", "price": 25.00}]
        
        result = checkout_message(fake_cart, fake_products)
        
        self.assertIsInstance(result, str)
        self.assertIn("50.00", result)
        self.assertIn("Items: 2", result)

    def test_display_genai_advice_ui(self):
        """Tests that the UI helper for GenAI handles empty states gracefully."""
        # Using a simple mock for the streamlit 'st' object
        with patch('modules.st') as mock_st:
            # Call with dummy data
            display_genai_advice("2026-03-24", "Wear a hat!", None)
            
            # Verify that streamlit tried to write the title and advice
            mock_st.title.assert_called()
            mock_st.write.assert_called_with("Wear a hat!")

if __name__ == "__main__":
    unittest.main()

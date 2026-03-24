#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py using mocking to avoid 
# real database and API calls (Safe for GitHub Actions).
#############################################################################
import unittest
from unittest.mock import patch
import data_fetcher

class TestDataFetcher(unittest.TestCase):

    @patch('data_fetcher.bq_client')
    def test_get_products(self, mock_bq):
        """Tests fetching a list of products using a mocked BigQuery client."""
        # Create fake database rows
        mock_bq.query.return_value.result.return_value = [
            {"product_id": "h1", "product_name": "Mock Hat", "price": 20.0}
        ]
        
        products = data_fetcher.get_products()
        
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["product_id"], "h1")
        mock_bq.query.assert_called_once() # Ensures BigQuery was "called"

    @patch('data_fetcher.bq_client')
    def test_get_product_by_id(self, mock_bq):
        """Tests fetching a single product."""
        test_id = "hat-001" 
        # Fake the response for a specific ID
        mock_bq.query.return_value.result.return_value = [
            {"product_id": test_id, "product_name": "Test Hat"}
        ]
        
        product = data_fetcher.get_product(test_id)
        
        self.assertIsNotNone(product)
        self.assertEqual(product["product_id"], test_id)

    @patch('data_fetcher.bq_client')
    def test_get_user_not_found(self, mock_bq):
        """Tests that a non-existent user returns None."""
        # Fake an empty database response
        mock_bq.query.return_value.result.return_value = []
        
        user = data_fetcher.get_user("fake_user_id_999")
        self.assertIsNone(user)

    @patch('data_fetcher.bq_client')
    def test_get_cart_returns_list(self, mock_bq):
        """Tests that cart retrieval returns a list."""
        mock_bq.query.return_value.result.return_value = [{"product_id": "h1", "qty": 1}]
        
        cart = data_fetcher.get_cart("test_user")
        self.assertIsInstance(cart, list)

    @patch('data_fetcher.bq_client')
    def test_get_orders(self, mock_bq):
        """Tests that order retrieval returns a list."""
        mock_bq.query.return_value.result.return_value = [{"order_id": "123", "user_id": "test_user"}]
        
        orders = data_fetcher.get_orders("test_user")
        self.assertIsInstance(orders, list)

    # We mock the AI model, AND the cart/order functions it relies on
    @patch('data_fetcher.genai_model')
    @patch('data_fetcher.get_orders')
    @patch('data_fetcher.get_cart')
    def test_genai_recommendation_structure(self, mock_get_cart, mock_get_orders, mock_genai):
        """Tests that the AI returns the expected dictionary structure."""
        user_id = "test_user"
        
        # Setup fake returns for the helper functions
        mock_get_cart.return_value = []
        mock_get_orders.return_value = []
        mock_genai.generate_content.return_value.text = "Mocked AI Advice"
        
        result = data_fetcher.get_genai_recommendations(user_id)
        
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["recommendations"], "Mocked AI Advice")

if __name__ == "__main__":
    unittest.main()

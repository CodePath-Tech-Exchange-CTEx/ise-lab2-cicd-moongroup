#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
import data_fetcher  # Ensure this file is in the same folder

class TestDataFetcher(unittest.TestCase):

    def test_get_products(self):
        """Tests that we can fetch a list of products from BigQuery."""
        products = data_fetcher.get_products()
        # Check that it returns a list
        self.assertIsInstance(products, list)
        # If there is data, check that the first item is a dictionary
        if len(products) > 0:
            self.assertIsInstance(products[0], dict)
            self.assertIn("product_id", products[0])

    def test_get_product_by_id(self):
        """Tests fetching a single product. 
        Note: You'll need a real product_id from your DB for this to pass."""
        # Replace 'hat-001' with an ID actually in your products table
        test_id = "hat-001" 
        product = data_fetcher.get_product(test_id)
        
        if product:
            self.assertEqual(product["product_id"], test_id)
            self.assertIn("product_name", product)

    def test_get_user_not_found(self):
        """Tests that a non-existent user returns None."""
        user = data_fetcher.get_user("fake_user_id_999")
        self.assertIsNone(user)

    def test_get_cart_returns_list(self):
        """Tests that cart retrieval always returns a list, even if empty."""
        cart = data_fetcher.get_cart("test_user")
        self.assertIsInstance(cart, list)

    def test_genai_recommendation_structure(self):
        """Tests that the AI returns the expected dictionary structure."""
        # This will actually call Vertex AI, so it might take a second!
        user_id = "test_user"
        result = data_fetcher.get_genai_recommendations(user_id)
        
        self.assertIn("user_id", result)
        self.assertIn("recommendations", result)
        self.assertEqual(result["user_id"], user_id)
        # Ensure recommendations is a string (since it's response.text)
        self.assertIsInstance(result["recommendations"], str)

if __name__ == "__main__":
    unittest.main()

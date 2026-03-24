import unittest
import math
import sys
import os
# This tells the GitHub runner: "Look in the current folder for files!"
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

# Update the keys to match BigQuery
REQUIRED_KEYS = {"product_id", "product_name", "description", "price", "image"}

def test_load_products_is_valid():
    products = load_products() # This now calls data_fetcher.get_products()
    assert isinstance(products, list)
    # Instead of '== 3', just make sure we got SOMETHING back
    assert len(products) > 0 

def test_get_product_by_id_found():
    products = load_products()
    if len(products) > 0:
        target = products[0]
        # Use 'product_id' because that's what BigQuery uses
        found = get_product_by_id(products, target["product_id"])
        assert found is not None
        assert found["product_id"] == target["product_id"]

def test_calc_total_basic():
    products = load_products()
    if len(products) > 0:
        first_product = products[0]
        pid = first_product["product_id"]
        price = first_product["price"]
        
        cart = {pid: 1} # Put 1 of the real product in the cart
        total = calc_total(cart, products)
        assert math.isclose(total, price, rel_tol=1e-9)




def test_add_to_cart_new_item():
    cart = init_cart()
    add_to_cart(cart, "h001", qty=1)
    assert cart == {"h001": 1}

def test_checkout_message():
    # We create the 'fake' data the function needs to run
    fake_cart = {"h001": 2}
    fake_products = [{"id": "h001", "name": "Howard Cap", "price": 25.00}]
    
    # We MUST pass both variables into the parentheses here
    result = checkout_message(fake_cart, fake_products)
    
    assert isinstance(result, str)
    assert "50.00" in result  # 2 hats at $25.00 = $50.00

def test_display_genai_advice_returns_none(monkeypatch):
    import modules # Import locally to force the linter to see it
    class DummySt:
        def title(self, *a, **k): pass
        def caption(self, *a, **k): pass
        def image(self, *a, **k): pass
        def info(self, *a, **k): pass
        def write(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def divider(self, *a, **k): pass

    # This fixes the 'NameError: modules is not defined'
    monkeypatch.setattr(modules, "st", DummySt())

    result = display_genai_advice("2026-03-13", "Looks good!", None)
    assert result is None

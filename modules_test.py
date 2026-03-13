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

REQUIRED_KEYS = {"id", "name", "description", "price", "image"}

def test_load_products_returns_list_of_three():
    products = load_products()
    assert isinstance(products, list)
    assert len(products) == 3

def test_get_product_by_id_found():
    products = load_products()
    target = products[0]
    found = get_product_by_id(products, target["id"])
    assert found is not None
    assert found["id"] == target["id"]

def test_add_to_cart_new_item():
    cart = init_cart()
    add_to_cart(cart, "h001", qty=1)
    assert cart == {"h001": 1}

def test_calc_total_basic():
    products = load_products()
    cart = {"h001": 1}
    p1 = get_product_by_id(products, "h001")["price"]
    total = calc_total(cart, products)
    assert math.isclose(total, p1, rel_tol=1e-9)

def test_checkout_message():
    fake_cart = {"h001": 1}
    fake_products = [{"id": "h001", "name": "Test Hat", "price": 10.00}]
    result = checkout_message(fake_cart, fake_products)
    assert isinstance(result, str)
    assert "1" in result

def test_display_genai_advice_returns_none(monkeypatch):
    class DummySt:
        def title(self, *a, **k): pass
        def caption(self, *a, **k): pass
        def image(self, *a, **k): pass
        def info(self, *a, **k): pass
        def write(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def divider(self, *a, **k): pass

    monkeypatch.setattr(modules, "st", DummySt()) # noqa: F821

    result = display_genai_advice(
        "2026-03-13", 
        "Great hat choice!", 
        None
    )
    assert result is None

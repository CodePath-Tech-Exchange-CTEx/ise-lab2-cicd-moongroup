#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
import copy
import math
from modules import (
    load_products,
    get_product_by_id,
    init_cart,
    add_to_cart,
    remove_from_cart,
    update_qty,
    calc_total,
    checkout_message,
)

# Write your tests below
'''
class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
'''


from modules import (
    load_products,
    get_product_by_id,
    init_cart,
    add_to_cart,
    remove_from_cart,
    update_qty,
    calc_total,
    checkout_message,
)

REQUIRED_KEYS = {"id", "name", "description", "price", "image"}


def test_load_products_returns_list_of_three():
    products = load_products()
    assert isinstance(products, list)
    assert len(products) == 3


def test_load_products_have_required_keys_and_types():
    products = load_products()
    for p in products:
        assert REQUIRED_KEYS.issubset(p.keys())
        assert isinstance(p["id"], str)
        assert isinstance(p["name"], str)
        assert isinstance(p["description"], str)
        assert isinstance(p["price"], (int, float))
        assert isinstance(p["image"], str)


def test_load_products_ids_unique():
    products = load_products()
    ids = [p["id"] for p in products]
    assert len(ids) == len(set(ids))


def test_get_product_by_id_found():
    products = load_products()
    target = products[0]
    found = get_product_by_id(products, target["id"])
    assert found is not None
    assert found["id"] == target["id"]


def test_get_product_by_id_not_found():
    products = load_products()
    found = get_product_by_id(products, "does_not_exist")
    assert found is None


def test_init_cart_empty_dict():
    cart = init_cart()
    assert isinstance(cart, dict)
    assert cart == {}


def test_add_to_cart_new_item():
    cart = init_cart()
    add_to_cart(cart, "h001", qty=1)
    assert cart == {"h001": 1}


def test_add_to_cart_increments_existing_item():
    cart = {"h001": 1}
    add_to_cart(cart, "h001", qty=2)
    assert cart["h001"] == 3


def test_remove_from_cart_existing_item():
    cart = {"h001": 2, "h002": 1}
    remove_from_cart(cart, "h001")
    assert "h001" not in cart
    assert cart == {"h002": 1}


def test_remove_from_cart_missing_item_no_crash():
    cart = {"h001": 2}
    remove_from_cart(cart, "h999")  # should do nothing
    assert cart == {"h001": 2}


def test_update_qty_sets_qty():
    cart = {"h001": 2}
    update_qty(cart, "h001", 5)
    assert cart["h001"] == 5


def test_update_qty_zero_removes_item():
    cart = {"h001": 2}
    update_qty(cart, "h001", 0)
    assert "h001" not in cart


def test_update_qty_negative_removes_item():
    cart = {"h001": 2}
    update_qty(cart, "h001", -3)
    assert "h001" not in cart


def test_calc_total_basic():
    products = load_products()
    cart = {"h001": 2, "h002": 1}

    # compute expected from product list
    p1 = get_product_by_id(products, "h001")["price"]
    p2 = get_product_by_id(products, "h002")["price"]
    expected = (p1 * 2) + (p2 * 1)

    total = calc_total(cart, products)
    assert math.isclose(total, expected, rel_tol=1e-9)


def test_calc_total_ignores_unknown_product_ids():
    products = load_products()
    cart = {"h999": 10}  # not in products
    total = calc_total(cart, products)
    assert total == 0.0


def test_checkout_message():
    assert checkout_message() == "Insufficient funds"


def test_display_genai_advice_returns_none(monkeypatch):
    # Mock streamlit calls so test can run without launching Streamlit
    class DummySt:
        def title(self, *a, **k): pass
        def caption(self, *a, **k): pass
        def image(self, *a, **k): pass
        def info(self, *a, **k): pass
        def write(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def divider(self, *a, **k): pass

    monkeypatch.setattr(modules, "st", DummySt())

    result = modules.display_genai_advice(
        "2026-02-28 11:05 AM",
        "Test advice content",
        "assets/motivation.jpg"
    )
    assert result is None    
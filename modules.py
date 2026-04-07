#############################################################################
# modules.py
#############################################################################

from internals import create_component
import streamlit as st
from typing import List, Dict, Optional, Any
from pathlib import Path  
import data_fetcher


# ---------------------------
# Product Data
# ---------------------------

def load_products(fetcher=data_fetcher.get_products):
    """
    Fetches products. Defaults to the real DB fetcher, 
    but allows a mock fetcher to be 'injected' for testing.
    """
    data = fetcher() 
    
    # FIX: don't remove product_id, just copy it
    for p in data:
        if "product_id" in p:
            p["id"] = p.get("product_id")
    return data


# ---------------------------
# Product Data
# ---------------------------

def get_product_by_id(products: List[Dict[str, Any]], product_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a single product dict by its id, or None if not found.
    """
    for product in products:
        if product.get("id") == product_id:
            return product
    return None


# ---------------------------
# Cart Logic
# ---------------------------

def init_cart():
    return {}


def add_to_cart(cart, product_id, qty=1):
    if product_id in cart:
        cart[product_id] += qty
    else:
        cart[product_id] = qty


def remove_from_cart(cart, product_id):
    if product_id in cart:
        del cart[product_id]


def update_qty(cart, product_id, qty):
    if qty <= 0:
        remove_from_cart(cart, product_id)
    else:
        cart[product_id] = qty


def calc_total(cart, products):
    total = 0.0
    for product_id, qty in cart.items():
        product = get_product_by_id(products, product_id)
        if product:
            total += product["price"] * qty
    return total


def count_cart_items(cart):
    total_qty = sum(cart.values())
    distinct_items = len(cart)
    return total_qty, distinct_items


def checkout_message(cart, products):
    total_qty, distinct_items = count_cart_items(cart)
    total = calc_total(cart, products)

    return (
        f"✅ You have successfully cashed out.\n\n"
        f"Items: {total_qty} (across {distinct_items} products)\n"
        f"Total: ${total:.2f}"
    )


# ---------------------------
# UI Helpers
# ---------------------------

def display_product_card(product):
    with st.container(border=True):
        try:
            st.image(product["image"], use_container_width=True)
        except Exception:
            st.write("(Image missing)")

        st.subheader(product["name"])
        st.write(product["description"])
        st.write(f"**${product['price']:.2f}**")

        view_clicked = st.button(
            "View Details",
            key=f"view_{product['id']}",
            use_container_width=True
        )
        return view_clicked


def display_product_grid(products):
    clicked_id = None
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            if display_product_card(product):
                clicked_id = product["id"]

    return clicked_id


def display_product_detail(product, cart):
    st.button("⬅️ Back to Home", key="back_home")

    st.title(product["name"])
    try:
        st.image(product["image"], use_container_width=True)
    except Exception:
        st.write("(Image missing)")

    st.write(product["description"])
    st.write(f"### ${product['price']:.2f}")

    qty = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)

    if st.button("Add to Cart", use_container_width=True):
        add_to_cart(cart, product["id"], int(qty))
        st.success("Added to cart!")


def display_recent_activity(order_history):
    st.title("Recent Activity")
    
    if not order_history:
        st.info("No recent purchases yet.")
        return

    for order in order_history:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"Order: {order.get('item_name')}")
                st.caption(f"Date: {order.get('date')}")
                st.write("📍 Location: Store Pickup")
            with col2:
                price = order.get('calories_burned', 0.0)
                qty = order.get('steps', 0)
                st.write(f"**${price:.2f}**")
                st.write(f"Qty: {qty}")


def display_cart_page(cart, products):
    if "order_history" not in st.session_state:
        st.session_state.order_history = []

    st.title("Your Cart")

    if st.session_state.get("checkout_success_msg"):
        st.success(st.session_state.checkout_success_msg)
        st.session_state.checkout_success_msg = None

    if not cart:
        st.info("Your cart is empty.")
        return

    for product_id, qty in list(cart.items()):
        product = get_product_by_id(products, product_id)
        if not product:
            continue

        with st.container(border=True):
            cols = st.columns([1, 3, 1, 1])
            with cols[0]:
                try:
                    st.image(product["image"], use_container_width=True)
                except:
                    st.write("")
            with cols[1]:
                st.write(f"**{product['name']}**")
                st.write(f"${product['price']:.2f}")
            with cols[2]:
                new_qty = st.number_input("Qty", min_value=0, max_value=20, value=int(qty), key=f"qty_{product_id}")
                update_qty(cart, product_id, int(new_qty))
            with cols[3]:
                if st.button("Remove", key=f"rm_{product_id}"):
                    remove_from_cart(cart, product_id)
                    st.rerun()

    total = calc_total(cart, products)
    st.write(f"## Total: ${total:.2f}")

    if st.button("Checkout", use_container_width=True):
        total_val = calc_total(cart, products)
        total_qty, _ = count_cart_items(cart)
        
        new_order = {
            "item_name": "Hat Order",
            "date": "2026-03-13",
            "calories_burned": total_val,
            "steps": total_qty,
        }
        
        st.session_state.order_history.append(new_order)
        
        msg = checkout_message(cart, products)
        st.session_state.checkout_success_msg = msg
        cart.clear()
        st.rerun()


def display_genai_advice(timestamp, content, motivational_image):
    st.title("Style Coach Advice")

    st.caption(f"Generated: {timestamp}")

    if motivational_image:
        try:
            if isinstance(motivational_image, str) and motivational_image.startswith(("http://", "https://")):
                st.image(motivational_image, use_container_width=True)
            else:
                img_path = Path(__file__).parent / motivational_image
                st.image(str(img_path), use_container_width=True)
        except Exception:
            st.info("(Motivational image unavailable)")

    # FIX: this is what test expects
    if content:
        st.write(content)
    else:
        st.warning("No advice content to display.")

    st.divider()

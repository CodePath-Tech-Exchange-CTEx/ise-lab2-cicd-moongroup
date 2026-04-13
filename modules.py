#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#############################################################################

import streamlit as st
from typing import List, Dict, Optional, Any
from pathlib import Path  
import data_fetcher


# ---------------------------
# Product Helpers
# ---------------------------

def load_products(fetcher=None):
    if fetcher is None:
        fetcher = data_fetcher.get_products

    data = fetcher()

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

def init_cart() -> Dict[str, int]:
    """Returns a new empty cart. Cart structure: {product_id: quantity}"""
    return {}


def add_to_cart(cart: Dict, product_id: str, qty: int = 1):
    """Adds a product to the cart or increases its quantity."""
    if product_id in cart:
        cart[product_id] += qty
    else:
        cart[product_id] = qty


def remove_from_cart(cart: Dict, product_id: str):
    """Removes a product completely from the cart."""
    if product_id in cart:
        del cart[product_id]


def update_qty(cart: Dict, product_id: str, qty: int):
    """Updates the quantity of a product. If qty <= 0, removes it."""
    if qty <= 0:
        remove_from_cart(cart, product_id)
    else:
        cart[product_id] = qty


def calc_total(cart: Dict, products: List[Dict]) -> float:
    """Calculates total cart value using product prices."""
    total = 0.0
    for product_id, qty in cart.items():
        product = get_product_by_id(products, product_id)
        if product:
            total += product["price"] * qty
    return total


def count_cart_items(cart: Dict):
    """Returns (total_qty, distinct_items)."""
    total_qty = sum(cart.values())
    distinct_items = len(cart)
    return total_qty, distinct_items


def checkout_message(cart: Dict, products: List[Dict]) -> str:
    """Builds a success message with item count + total."""
    total_qty, distinct_items = count_cart_items(cart)
    total = calc_total(cart, products)
    return (
        f"✅ You have successfully checked out.\n\n"
        f"Items: {total_qty} (across {distinct_items} products)\n"
        f"Total: ${total:.2f}"
    )


# ---------------------------
# Product Catalog UI
# ---------------------------

def display_product_card(product: Dict) -> bool:
    """
    Shows one product card.
    Returns True if the user clicked 'View Details'.
    """
    with st.container(border=True):
        try:
            st.image(product["image"], use_container_width=True)
        except Exception:
            st.write("(Image unavailable)")

        st.subheader(product["name"])
        st.write(product["description"])
        st.write(f"**${product['price']:.2f}**")

        return st.button(
            "View Details",
            key=f"view_{product['id']}",
            use_container_width=True,
        )


def display_product_grid(products: List[Dict]) -> Optional[str]:
    """
    Shows products in a 3-column grid.
    Returns product_id if a product was clicked, else None.
    """
    if not products:
        st.info("No products available right now.")
        return None

    clicked_id = None
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            if display_product_card(product):
                clicked_id = product["id"]

    return clicked_id


# ---------------------------
# Product Detail UI
# ---------------------------

def display_product_detail(product: Dict, cart: Dict):
    """Shows the full product detail view with Add to Cart."""
    # Back button — routing handled in app.py via session_state key
    st.button("⬅️ Back to Home", key="back_home")

    st.title(product["name"])

    try:
        st.image(product["image"], use_container_width=True)
    except Exception:
        st.write("(Image unavailable)")

    st.write(product["description"])
    st.write(f"### ${product['price']:.2f}")

    qty = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)

    if st.button("Add to Cart", use_container_width=True):
        add_to_cart(cart, product["id"], int(qty))
        st.success(f"Added {int(qty)}× {product['name']} to cart!")


# ---------------------------
# Cart UI
# ---------------------------

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

def display_cart_page(cart: Dict, products: List[Dict], user_id: str = "user1"):
    """
    Shows cart contents, totals, and checkout.
    Writes quantity changes back to BigQuery via data_fetcher helpers.
    """
    if "order_history" not in st.session_state:
        st.session_state.order_history = []

    # Import write helpers here to avoid circular imports at module level
    from data_fetcher import upsert_cart_item, delete_cart_item, clear_cart

    st.title("🛒 Your Cart")

    # Show any pending checkout success message
    st.success("Added to cart!")

    if st.session_state.get("checkout_success_msg"):
        st.success(st.session_state.checkout_success_msg)
        st.session_state.checkout_success_msg = None

    if not cart:
        st.info("Your cart is empty. Head back to the catalog to add some hats!")
        return

    # --- Line items ---
    for product_id, qty in list(cart.items()):
        product = get_product_by_id(products, product_id)
        if not product:
            continue

        with st.container(border=True):
            cols = st.columns([1, 3, 1, 1])

            with cols[0]:
                try:
                    st.image(product["image"], use_container_width=True)
                except Exception:
                    st.write("")

            with cols[1]:
                st.write(f"**{product['name']}**")
                st.write(f"${product['price']:.2f} each")
                st.write(f"Subtotal: **${product['price'] * qty:.2f}**")

            with cols[2]:
                new_qty = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=20,
                    value=int(qty),
                    key=f"qty_{product_id}",
                )
                if int(new_qty) != int(qty):
                    update_qty(cart, product_id, int(new_qty))
                    # Sync to DB: upsert handles qty=0 as delete
                    upsert_cart_item(user_id, product_id, int(new_qty))
                    st.rerun()

            with cols[3]:
                if st.button("Remove", key=f"rm_{product_id}"):
                    remove_from_cart(cart, product_id)
                    delete_cart_item(user_id, product_id)
                    st.rerun()

    st.divider()
    total = calc_total(cart, products)
    st.write(f"## Total: ${total:.2f}")

    # --- Checkout ---
    if st.button("✅ Checkout", use_container_width=True):
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
        # Clear cart in DB and in session
        try:
            clear_cart(user_id)
        except Exception as e:
            st.warning(f"Could not clear cart from database: {e}")
        cart.clear()
        st.session_state.checkout_success_msg = msg
        st.rerun()


# ---------------------------
# Orders UI
# ---------------------------

def display_orders_page(orders: List[Dict], products: List[Dict]):
    """
    Displays the full orders history page.
    Handles flexible BigQuery column names for order_id, date, product, qty, total.
    """
    st.title("📦 Your Orders")

    if not orders:
        st.info("You haven't placed any orders yet.")
        return

    product_lookup = {p["id"]: p for p in products}

    for order in orders:
        with st.container(border=True):
            # Flexible field resolution
            order_id   = order.get("order_id") or order.get("id") or "N/A"
            order_date = order.get("order_date") or order.get("date") or "N/A"
            product_id = order.get("product_id") or order.get("item_id")
            quantity   = order.get("quantity") or order.get("qty")
            status     = order.get("status")

            try:
                total = float(
                    order.get("total_amount")
                    or order.get("total")
                    or order.get("price")
                    or 0
                )
            except (TypeError, ValueError):
                total = 0.0

            col_left, col_right = st.columns([3, 1])

            with col_left:
                st.subheader(f"Order #{order_id}")
                st.caption(f"📅 {order_date}")

                if product_id and str(product_id) in product_lookup:
                    product = product_lookup[str(product_id)]
                    st.write(f"🧢 **{product['name']}**")
                    # Show thumbnail if available
                    try:
                        st.image(product["image"], width=80)
                    except Exception:
                        pass
                elif product_id:
                    st.write(f"Product ID: `{product_id}`")

                if quantity is not None:
                    st.write(f"Quantity: {quantity}")

                if status:
                    status_emoji = {
                        "delivered": "✅",
                        "shipped": "🚚",
                        "processing": "⏳",
                        "cancelled": "❌",
                    }.get(str(status).lower(), "📋")
                    st.write(f"Status: {status_emoji} {status}")

            with col_right:
                st.metric("Total", f"${total:.2f}")


# ---------------------------
# GenAI Style Coach UI
# ---------------------------

def display_genai_advice(timestamp: str, content: str, motivational_image: str):
    """
    Displays the GenAI Style Coach page.

    Args:
        timestamp: str  — when advice was generated
        content:   str  — advice text from Gemini
        motivational_image: str — local path or URL
    """
    st.title("💡 Style Coach")
    st.caption(f"Generated: {timestamp}")

    if motivational_image:
        try:
            if isinstance(motivational_image, str) and motivational_image.startswith(
                ("http://", "https://")
            ):
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
    st.caption("Tip: Pair your favorite cap with confidence — you got this. 🧢")
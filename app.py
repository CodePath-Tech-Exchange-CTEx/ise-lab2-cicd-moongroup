#############################################################################
# app.py
#
# Entrypoint for the Hat Plug Streamlit app.
# Connects live BigQuery data to all UI components.
#############################################################################

import streamlit as st
from datetime import datetime

import data_fetcher
from modules import (
    get_product_by_id,
    init_cart,
    display_product_detail,
    display_cart_page,
    display_orders_page,
    display_genai_advice,
    display_reviews_section,
    inject_css,
)
from catalog_filter import display_catalog_filter
from data_fetcher import (
    get_products,
    get_cart,
    get_orders,
    get_genai_recommendations,
)

# ─────────────────────────────────────────────
# Page config — MUST be the very first st call
# ─────────────────────────────────────────────
st.set_page_config(page_title="Hat Plug", layout="wide", page_icon="🧢")

USER_ID      = "user1"
DEFAULT_IMAGE = "https://via.placeholder.com/300x300?text=No+Image"


# ─────────────────────────────────────────────
# Data normalisation
# ─────────────────────────────────────────────

def normalize_products(rows):
    """
    Converts raw BigQuery rows into the standard product dict.
    Preserves color, style, stock so catalog_filter can use them.
    """
    products = []
    for row in rows or []:
        product_id = row.get("product_id") or row.get("id")
        if not product_id:
            continue
        try:
            price = float(row.get("price", 0) or 0)
        except (TypeError, ValueError):
            price = 0.0
        try:
            stock = int(row.get("stock", 0) or 0)
        except (TypeError, ValueError):
            stock = 0

        products.append({
            "id":          str(product_id),
            "product_id":  str(product_id),
            "name":        row.get("name") or "Untitled Product",
            "description": row.get("description") or "",
            "price":       price,
            "stock":       stock,
            "color":       row.get("color") or "",
            "style":       row.get("style") or "",
            # support both image_url (BigQuery) and image (legacy)
            "image":       (
                row.get("image_url")
                or row.get("image")
                or row.get("imageUrl")
                or DEFAULT_IMAGE
            ),
            "image_url":   (
                row.get("image_url")
                or row.get("image")
                or DEFAULT_IMAGE
            ),
        })
    return products


def cart_rows_to_dict(rows):
    """Converts raw BigQuery cart rows into {product_id: qty} dict."""
    cart = {}
    for row in rows or []:
        product_id = row.get("product_id") or row.get("id")
        qty = row.get("quantity") or row.get("qty") or row.get("count") or 1
        if not product_id:
            continue
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1
        if qty > 0:
            cart[str(product_id)] = qty
    return cart


# ─────────────────────────────────────────────
# Data loaders
# ─────────────────────────────────────────────

def load_live_products():
    """Fetches all products from BigQuery and normalises them."""
    try:
        rows = get_products()
        return normalize_products(rows)
    except Exception as e:
        st.warning(f"Could not load products from the database: {e}")
        return [
            {
                "id": "h001", "product_id": "h001",
                "name": "Howard Classic Cap",
                "description": "A classic maroon Howard cap with everyday style.",
                "price": 35.00, "stock": 10, "color": "Red", "style": "Snapback",
                "image": DEFAULT_IMAGE, "image_url": DEFAULT_IMAGE,
            },
            {
                "id": "h002", "product_id": "h002",
                "name": "Bison Snapback",
                "description": "Structured snapback with a clean streetwear look.",
                "price": 40.00, "stock": 5, "color": "Black", "style": "Snapback",
                "image": DEFAULT_IMAGE, "image_url": DEFAULT_IMAGE,
            },
            {
                "id": "h003", "product_id": "h003",
                "name": "HU Vintage Hat",
                "description": "Vintage-inspired cap with a relaxed fit.",
                "price": 32.00, "stock": 0, "color": "Beige", "style": "Fitted",
                "image": DEFAULT_IMAGE, "image_url": DEFAULT_IMAGE,
            },
        ]


def sync_db_cart_into_session():
    """
    Merges the DB cart into the session cart on page load.
    Items already in session are not overwritten so local edits survive.
    """
    try:
        db_cart = cart_rows_to_dict(get_cart(USER_ID))
        for product_id, qty in db_cart.items():
            if product_id not in st.session_state.cart:
                st.session_state.cart[product_id] = qty
    except Exception as e:
        st.warning(f"Could not load cart from the database: {e}")


def load_live_advice():
    """Generates GenAI style advice via Vertex AI / Gemini."""
    try:
        cart_enriched = [
            {
                "name": next((p["name"] for p in products if p["id"] == pid), pid),
                "style": next((p.get("style", "") for p in products if p["id"] == pid), ""),
                "color": next((p.get("color", "") for p in products if p["id"] == pid), ""),
                "quantity": qty,
            }
            for pid, qty in st.session_state.cart.items()
        ]
        result = get_genai_recommendations(USER_ID, cart_items=cart_enriched)
        return result.get("recommendations", "No style advice returned.")
    except Exception as e:
        return f"Could not load live style advice right now.\n\n{e}"


# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None

if "cart" not in st.session_state:
    st.session_state.cart = init_cart()

if "advice_timestamp" not in st.session_state:
    st.session_state.advice_timestamp = "Not generated yet"

if "advice_content" not in st.session_state:
    st.session_state.advice_content = (
        "Click the button below to generate live style advice."
    )

if "advice_image" not in st.session_state:
    st.session_state.advice_image = "assets/coach.jpg"

if "reviews" not in st.session_state:
    st.session_state.reviews = {
        "h001": [
            {
                "name": "Alex M.", "email": "alex@email.com",
                "rating": 5, "text": "Great quality and the fit was perfect.",
                "verified": True, "fit": "Excellent", "quality": "Excellent",
                "shipping": "Fast",
            },
            {
                "name": "Jordan T.", "email": "jordan@email.com",
                "rating": 4, "text": "Nice hat and arrived on time.",
                "verified": False, "fit": "Good", "quality": "Good",
                "shipping": "On time",
            },
        ]
    }


# ─────────────────────────────────────────────
# Load products (every render)
# ─────────────────────────────────────────────

products = load_live_products()
inject_css()

# ─────────────────────────────────────────────
# Top navigation bar
# ─────────────────────────────────────────────

nav = st.columns([4, 1, 1, 1])

with nav[0]:
    if st.button("🧢 Hat Plug", key="nav_home"):
        st.session_state.page = "home"
        st.rerun()

with nav[1]:
    if st.button("💡 Style Coach", use_container_width=True):
        st.session_state.page = "advice"
        st.rerun()

with nav[2]:
    if st.button("📦 Orders", use_container_width=True):
        st.session_state.page = "orders"
        st.rerun()

with nav[3]:
    cart_count = sum(st.session_state.cart.values())
    cart_label = f"🛒 Cart ({cart_count})" if cart_count else "🛒 Cart"
    if st.button(cart_label, use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()

st.divider()


# ─────────────────────────────────────────────
# Routing
# ─────────────────────────────────────────────

# ── Home / Catalog (now with filters) ────────
if st.session_state.page == "home":
    st.title("Hat Plug 🧢")
    st.caption("Find your perfect cap.")

    clicked_id = display_catalog_filter(products, st.session_state.cart)
    if clicked_id:
        st.session_state.selected_product_id = clicked_id
        st.session_state.page = "detail"
        st.rerun()


# ── Product Detail ────────────────────────────
elif st.session_state.page == "detail":
    product = get_product_by_id(products, st.session_state.selected_product_id)

    if not product:
        st.error("Product not found.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    else:
        # back_home button is rendered inside display_product_detail
        if st.session_state.get("back_home"):
            st.session_state.page = "home"
            st.session_state.back_home = False
            st.rerun()

        display_product_detail(product, st.session_state.cart)
        display_reviews_section(product["id"])


# ── Cart ──────────────────────────────────────
elif st.session_state.page == "cart":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    sync_db_cart_into_session()
    display_cart_page(st.session_state.cart, products, user_id=USER_ID)


# ── Orders ────────────────────────────────────
elif st.session_state.page == "orders":
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    try:
        orders = get_orders(USER_ID)
    except Exception as e:
        st.error(f"Could not load orders from the database: {e}")
        orders = []

    display_orders_page(orders, products)


# ── Style Coach ───────────────────────────────
elif st.session_state.page == "advice":
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("✨ Generate Live Advice", use_container_width=True):
        with st.spinner("Asking your style coach…"):
            st.session_state.advice_content = load_live_advice()
            st.session_state.advice_timestamp = datetime.now().strftime(
                "%Y-%m-%d %I:%M %p"
            )
        st.rerun()

    display_genai_advice(
        st.session_state.advice_timestamp,
        st.session_state.advice_content,
        st.session_state.advice_image,
    )
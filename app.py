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
    display_product_grid,
    display_product_detail,
    display_cart_page,
    display_orders_page,       # ← now lives in modules.py
    display_genai_advice,
)
from data_fetcher import (
    get_products,
    get_cart,
    get_orders,
    get_genai_recommendations,
)

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
st.set_page_config(page_title="Hat Plug", layout="wide")
st.markdown("""
<style>
body {
    background-color: #f5f5f5;
}

.main {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
}

h1 {
    color: #2c3e50;
    text-align: center;
}

.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.advice-text {
    font-size: 18px;
    font-weight: 500;
    color: #333;
}
</style>
""", unsafe_allow_html=True)
#  1. Page Configuration (MUST be first Streamlit command)
st.set_page_config(page_title="HU Store", layout="wide", page_icon="🧢")

USER_ID = "user1"
DEFAULT_IMAGE = "https://via.placeholder.com/300x300?text=No+Image"


# ─────────────────────────────────────────────
# Data normalisation helpers
# ─────────────────────────────────────────────

def normalize_products(rows):
    """Converts raw BigQuery rows into the standard product dict format."""
    products = []
    for row in rows or []:
        product_id = row.get("product_id") or row.get("id")
        if not product_id:
            continue
        try:
            price = float(row.get("price", 0) or 0)
        except (TypeError, ValueError):
            price = 0.0
        products.append(
            {
                "id": str(product_id),
                "name": row.get("name") or "Untitled Product",
                "description": row.get("description") or "",
                "price": price,
                "image": (
                    row.get("image_url")
                    or row.get("image")
                    or row.get("imageUrl")
                    or DEFAULT_IMAGE
                ),
            }
        )
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
        st.error(f"Could not load products from the database: {e}")
        return []


def sync_db_cart_into_session():
    """
    Merges the DB cart into the session cart on page load.
    DB rows that are already in session_state are skipped so local
    quantity edits are not overwritten mid-session.
    """
    try:
        db_cart_rows = get_cart(USER_ID)
        db_cart = cart_rows_to_dict(db_cart_rows)
        for product_id, qty in db_cart.items():
            if product_id not in st.session_state.cart:
                st.session_state.cart[product_id] = qty
    except Exception as e:
        st.warning(f"Could not load cart from the database: {e}")


def load_live_advice():
    """Generates GenAI style advice via Vertex AI / Gemini."""
    try:
        result = get_genai_recommendations(USER_ID)
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
    st.session_state.advice_image = "assets/motivation.JPG"


# ─────────────────────────────────────────────
# Load live product data (every render)
# ─────────────────────────────────────────────

products = load_live_products()


# ─────────────────────────────────────────────
# Top navigation bar
# ─────────────────────────────────────────────

top = st.columns([4, 1, 1, 1])

with top[0]:
    if st.button("🧢 Hat Plug", key="nav_home"):
        st.session_state.page = "home"
        st.rerun()

with top[1]:
    if st.button("💡 Style Coach", use_container_width=True):
        st.session_state.page = "advice"
        st.rerun()

with top[2]:
    if st.button("📦 Orders", use_container_width=True):
        st.session_state.page = "orders"
        st.rerun()

with top[3]:
    cart_count = sum(st.session_state.cart.values())
    cart_label = f"🛒 Cart ({cart_count})" if cart_count else "🛒 Cart"
    if st.button(cart_label, use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()

st.divider()

#  7. Routing Logic

if st.session_state.page == "home":
    st.title("Hat Plug 🧢")
    st.caption("Find your perfect cap.")

    clicked_id = display_product_grid(products)
    if clicked_id:
        st.session_state.selected_product_id = clicked_id
        st.session_state.page = "detail"
        st.rerun()


# ── Product Detail ───────────────────────────
elif st.session_state.page == "detail":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

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

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💡 Get Style Advice", use_container_width=True):
                st.session_state.page = "advice"
                st.rerun()
        with col2:
            if st.button("🛒 Go to Cart", use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()


# ── Cart ─────────────────────────────────────
elif st.session_state.page == "cart":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    # Merge DB cart into session (picks up items added on other devices / sessions)
    sync_db_cart_into_session()

    display_cart_page(st.session_state.cart, products, user_id=USER_ID)


# ── Orders ───────────────────────────────────
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


# ── Style Coach / GenAI Advice ───────────────
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
    if "advice_data" not in st.session_state:
        st.session_state.advice_data = None

    display_genai_advice(
        None,  # timestamp (missing in my data)
        data.get("recommendations"),
        "https://i.pinimg.com/736x/3c/8a/ea/3c8aea98d9047f1fc9cc08c730b88c30.jpg"
    )
 

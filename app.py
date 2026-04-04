#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
import data_fetcher  # Import to connect to BigQuery/Vertex AI
from modules import (
    load_products, 
    get_product_by_id,
    init_cart, 
    display_product_grid,
    display_product_detail, 
    display_cart_page,
    display_genai_advice,
)

#  1. Page Configuration (MUST be first Streamlit command)
st.set_page_config(page_title="HU Store", layout="wide", page_icon="🧢")

#  2. Custom Font + UI Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* Apply font globally */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Header styling */
h1, h2, h3, h4 {
    font-weight: 600;
}

/* Add spacing to main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

#  3. Efficient Data Loading
@st.cache_data
def get_all_products():
    return load_products()

products = get_all_products()

#  4. Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None

if "cart" not in st.session_state:
    st.session_state.cart = init_cart()

#  5. Fetch AI advice once per session
if "advice_data" not in st.session_state:
    try:
        st.session_state.advice_data = data_fetcher.get_genai_recommendations("user1")
    except Exception:
        st.session_state.advice_data = {
            "recommendations": "Stick to the classics. A well-fitted HU cap goes with everything!",
            "user_id": "user1"
        }

#  6. Top Navigation Bar
top = st.columns([4, 1, 1]) 

with top[0]:
    st.title("Campus Store")

with top[1]:
    if st.button("💡 Style Coach", use_container_width=True):
        st.session_state.page = "advice"
        st.rerun()

with top[2]:
    cart_count = sum(st.session_state.cart.values())
    if st.button(f"🛒 Cart ({cart_count})", use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()

st.divider()

#  7. Routing Logic

if st.session_state.page == "home":
    clicked_id = display_product_grid(products)
    if clicked_id:
        st.session_state.selected_product_id = clicked_id
        st.session_state.page = "detail"
        st.rerun()

elif st.session_state.page == "detail":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    product = get_product_by_id(products, st.session_state.selected_product_id)
    display_product_detail(product, st.session_state.cart)

elif st.session_state.page == "cart":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    display_cart_page(st.session_state.cart, products)

elif st.session_state.page == "advice":
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    display_genai_advice(st.session_state.advice_data)

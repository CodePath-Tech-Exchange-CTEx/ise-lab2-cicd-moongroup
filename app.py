#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################
'''
import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name')
    display_my_custom_component(value)


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()

'''    

import streamlit as st
from modules import (
    load_products, get_product_by_id,
    init_cart, display_product_grid,
    display_product_detail, display_cart_page,
    display_genai_advice,                 # <<< ADDED
)
st.set_page_config(page_title="Store", layout="wide")

# Session state init
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None
if "cart" not in st.session_state:
    st.session_state.cart = init_cart()

if "advice_timestamp" not in st.session_state:
    st.session_state.advice_timestamp = "2026-02-28 11:05 AM"
if "advice_content" not in st.session_state:
    st.session_state.advice_content = (
        "Pick one statement hat and keep the rest of your fit clean.\n"
        "If you go snapback, match it with a neutral hoodie or tee.\n"
        "Confidence is the best accessory."
    )
if "advice_image" not in st.session_state:
    st.session_state.advice_image = "assets/motivation.JPG"  # change if needed


products = load_products()

# Top bar
top = st.columns([5, 1, 1])  # <<< CHANGED (added a column)
with top[0]:
    st.title("HomePage")

with top[1]:
    if st.button("💡 Style Coach", use_container_width=True):  # <<< ADDED
        st.session_state.page = "advice"
        st.rerun()

with top[2]:
    if st.button("🛒 Cart", use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()
# Routing
if st.session_state.page == "home":
    clicked_id = display_product_grid(products)
    if clicked_id:
        st.session_state.selected_product_id = clicked_id
        st.session_state.page = "detail"
        st.rerun()

elif st.session_state.page == "detail":
    product = get_product_by_id(products, st.session_state.selected_product_id)
    if not product:
        st.error("Product not found.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    else:
        # back button lives inside detail UI; handle it here:
        # (Streamlit buttons return True only on click, so we check the key)
        if st.session_state.get("back_home"):
            st.session_state.page = "home"
            st.session_state.back_home = False
            st.rerun()

        display_product_detail(product, st.session_state.cart)

         # <<< ADDED: optional quick link to advice from detail
        if st.button("Get Style Advice", use_container_width=True):
            st.session_state.page = "advice"
            st.rerun()

        if st.button("Go to Cart", use_container_width=True):
            st.session_state.page = "cart"
            st.rerun()

elif st.session_state.page == "cart":
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    display_cart_page(st.session_state.cart, products)

elif st.session_state.page == "advice":  # <<< ADDED
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    display_genai_advice(
        st.session_state.advice_timestamp,
        st.session_state.advice_content,
        st.session_state.advice_image
    )    

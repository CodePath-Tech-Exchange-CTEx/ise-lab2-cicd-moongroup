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

# 1. Page Configuration
st.set_page_config(page_title="HU Store", layout="wide", page_icon="🧢")

# 2. Efficient Data Loading
# This prevents the app from re-querying the database on every single click.
@st.cache_data
def get_all_products():
    return load_products()

products = get_all_products()

# 3. Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None
if "cart" not in st.session_state:
    st.session_state.cart = init_cart()

# Fetch AI advice once per session
if "advice_data" not in st.session_state:
    try:
        # Tries to get real AI recommendations for the user
        st.session_state.advice_data = data_fetcher.get_genai_recommendations("user1")
    except Exception:
        # Fallback if the AI service is unavailable or not configured
        st.session_state.advice_data = {
            "recommendations": "Stick to the classics. A well-fitted HU cap goes with everything!",
            "user_id": "user1"
        }

# 4. Top Navigation Bar
top = st.columns([4, 1, 1]) 
with top[0]:
    st.title("HU Campus Store")

with top[1]:
    if st.button("💡 Style Coach", use_container_width=True):
        st.session_state.page = "advice"
        st.rerun()

with top[2]:
    # Dynamic cart count on the button
    cart_count = sum(st.session_state.cart.values())
    if st.button(f"🛒 Cart ({cart_count})", use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()

st.divider()

# 5. Routing Logic
# This acts as the "Traffic Controller" for your app's different views.

if st.session_state.page == "home":
    # display_product_grid returns the ID of whatever was clicked
    clicked_id = display_product_grid(products)
    if clicked_id:
        st.session_state.selected_product_id = clicked_id
        st.session_state.page = "detail"
        st.rerun()

elif st.session_state.page == "detail":
    # Navigation back button
    if st.button("⬅️ Back to Shop"):
        st.session_state.page = "home"
        st.rerun()

    product = get_product_by_id(products, st.session_state   

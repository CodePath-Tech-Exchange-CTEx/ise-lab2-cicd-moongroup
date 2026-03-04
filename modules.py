#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st
from typing import List, Dict, Optional, Any
from pathlib import Path  



# ---------------------------
# Product Data
# ---------------------------


'''
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)

def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass

def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass

def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass

def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
'''


def load_products() -> List[Dict[str, Any]]:
    """
    Returns the list of products for the store.

    For MVP speed, this is hard-coded.
    Later, you can replace this with a JSON/CSV load without changing other code.
    """
    return [
        {
            "id": "h001",
            "name": "Howard Classic Cap",
            "description": "Maroon dad hat with embroidered HU logo.",
            "price": 24.99,
            "image": "assets/h001.jpg",  # or an image URL
        },
        {
            "id": "h002",
            "name": "Streetwear Snapback",
            "description": "Flat brim snapback with adjustable strap.",
            "price": 29.99,
            "image": "assets/h002.jpg",
        },
        {
            "id": "h003",
            "name": "flower blossom",
            "description": "straight from japan.",
            "price": 19.99,
            "image": "assets/h003.jpg",
        },
    ]

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
    """
    Returns a new empty cart.
    Cart structure: {product_id: quantity}
    """
    return {}


def add_to_cart(cart, product_id, qty=1):
    """
    Adds a product to the cart or increases its quantity.
    """
    if product_id in cart:
        cart[product_id] += qty
    else:
        cart[product_id] = qty


def remove_from_cart(cart, product_id):
    """
    Removes a product completely from the cart.
    """
    if product_id in cart:
        del cart[product_id]


def update_qty(cart, product_id, qty):
    """
    Updates the quantity of a product.
    If qty <= 0, the product is removed.
    """
    if qty <= 0:
        remove_from_cart(cart, product_id)
    else:
        cart[product_id] = qty


def calc_total(cart, products):
    """
    Calculates total cart value using product prices.
    """
    total = 0.0
    for product_id, qty in cart.items():
        product = get_product_by_id(products, product_id)
        if product:
            total += product["price"] * qty
    return total

def count_cart_items(cart):
    """
    Returns (total_qty, distinct_items)
    total_qty = sum of quantities across all products
    distinct_items = number of unique product_ids in cart
    """
    total_qty = sum(cart.values())
    distinct_items = len(cart)
    return total_qty, distinct_items  # <<< ADDED    


def checkout_message(cart, products):
    """
    Builds a success message with item count + total.
    """
    total_qty, distinct_items = count_cart_items(cart)  # <<< CHANGED
    total = calc_total(cart, products)                  # <<< CHANGED

    return (
        f"✅ You have successfully cashed out.\n\n"
        f"Items: {total_qty} (across {distinct_items} products)\n"
        f"Total: ${total:.2f}"
    )  # <<< CHANGED


# ---------------------------
# UI Helpers (Homepage + Detail + Cart)
# ---------------------------

def display_product_card(product):
    """
    Shows one product card.
    Returns True if the user clicked 'View Details', False otherwise.
    """
    with st.container(border=True):
        # Image
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
    """
    Shows products in a 3-column grid.
    Returns product_id if a product was clicked, else None.
    """
    clicked_id = None
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            if display_product_card(product):
                clicked_id = product["id"]

    return clicked_id


def display_product_detail(product, cart):
    """
    Shows the product detail view + Add to Cart.
    """
    st.button("⬅️ Back to Home", key="back_home")  # app.py will handle routing

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


def display_cart_page(cart, products):
    """
    Shows cart contents + total + checkout button.
    """
    st.title("Your Cart")

        # show checkout message after rerun
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
                except Exception:
                    st.write("")

            with cols[1]:
                st.write(f"**{product['name']}**")
                st.write(f"${product['price']:.2f}")

            with cols[2]:
                new_qty = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=20,
                    value=int(qty),
                    step=1,
                    key=f"qty_{product_id}"
                )
                update_qty(cart, product_id, int(new_qty))

            with cols[3]:
                if st.button("Remove", key=f"rm_{product_id}"):
                    remove_from_cart(cart, product_id)
                    st.rerun()

    total = calc_total(cart, products)
    st.write(f"## Total: ${total:.2f}")

    if st.button("Checkout", use_container_width=True):
        msg = checkout_message(cart, products)     # <<< CHANGED
        st.session_state.checkout_success_msg = msg                           # <<< CHANGED
        cart.clear()                              # <<< ADDED (optional, but recommended)
        st.rerun()                                # <<< ADDED


def display_genai_advice(timestamp, content, motivational_image):
    """
    Displays a GenAI advice page/section.

    Input:
      - timestamp: str (e.g., "2026-02-28 11:05 AM")
      - content: str (advice text)
      - motivational_image: str (path like "assets/motivation.jpg" OR URL)

    Output:
      - None
    """
    st.title("Style Coach Advice")

    # Timestamp
    st.caption(f"Generated: {timestamp}")

    # Image
    if motivational_image:
        try:
            # Allow URLs OR local files
            if isinstance(motivational_image, str) and motivational_image.startswith(("http://", "https://")):
                st.image(motivational_image, use_container_width=True)
            else:
                # Resolve relative path based on modules.py location (not terminal cwd)
                img_path = Path(__file__).parent / motivational_image
                st.image(str(img_path), use_container_width=True)
        except Exception:
            st.info("(Motivational image unavailable)")

    # Advice content
    if content:
        st.write(content)
    else:
        st.warning("No advice content to display.")

    st.divider()
    st.write("Tip: Pair your favorite cap with confidence — you got this.")
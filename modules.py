#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#############################################################################
import os
import streamlit as st
from typing import List, Dict, Optional, Any
from pathlib import Path
import data_fetcher
 
 
# ---------------------------
# Shared CSS
# ---------------------------
 
HAT_SHOP_CSS = """
<style>
/* ── Boutique card ── */
.hs-card {
    background: #FAF6F0;
    border: 0.5px solid #C8B89A;
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.15s;
}
.hs-card:hover { border-color: #7B4F2E; }
 
/* ── Section eyebrow label ── */
.hs-eyebrow {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7B5B3A;
    margin-bottom: 0.5rem;
}
 
/* ── Price tag ── */
.hs-price {
    font-size: 20px;
    font-weight: 600;
    color: #5C3318;
    letter-spacing: -0.01em;
}
 
/* ── Badge pill ── */
.hs-badge {
    display: inline-block;
    background: #EFE8DC;
    color: #7B4F2E;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 6px;
}
 
/* ── Cart line ── */
.hs-cart-name {
    font-weight: 600;
    color: #2C1A0E;
    font-size: 15px;
}
.hs-cart-sub {
    color: #7B5B3A;
    font-size: 13px;
}
 
/* ── Order card header ── */
.hs-order-id {
    font-size: 13px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #7B5B3A;
}
 
/* ── Style coach ── */
.hs-coach-tip {
    background: #EFE8DC;
    border-left: 3px solid #7B4F2E;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
    font-size: 13px;
    color: #5C3318;
    margin-top: 1rem;
}
</style>
"""
 
 
def inject_css():
    """Inject hat-shop styles once per session."""
    if "_hs_css_injected" not in st.session_state:
        st.markdown(HAT_SHOP_CSS, unsafe_allow_html=True)
        st.session_state["_hs_css_injected"] = True
 
 
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
    Shows one product card with boutique styling.
    Returns True if the user clicked 'View Details'.
    """
    inject_css()
 
    is_new    = product.get("is_new", False)
    is_best   = product.get("is_bestseller", False)
 
    with st.container():
        st.markdown('<div class="hs-card">', unsafe_allow_html=True)
 
        try:
            image_path = os.path.join("assets", product["image"])
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.markdown(
                    '<div style="height:160px;background:#EFE8DC;border-radius:8px 8px 0 0;'
                    'display:flex;align-items:center;justify-content:center;'
                    'color:#A0785A;font-size:13px;">Image unavailable</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                '<div style="height:160px;background:#EFE8DC;border-radius:8px 8px 0 0;'
                'display:flex;align-items:center;justify-content:center;'
                'color:#A0785A;font-size:13px;">Image unavailable</div>',
                unsafe_allow_html=True,
            )
 
        # Badge row
        if is_new:
            st.markdown('<span class="hs-badge">New</span>', unsafe_allow_html=True)
        elif is_best:
            st.markdown('<span class="hs-badge">Bestseller</span>', unsafe_allow_html=True)
 
        st.subheader(product["name"])
        st.caption(product["description"])
 
        col_price, col_btn = st.columns([1, 1])
        with col_price:
            st.markdown(
                f'<p class="hs-price">${product["price"]:.2f}</p>',
                unsafe_allow_html=True,
            )
        with col_btn:
            clicked = st.button(
                "View Details",
                key=f"view_{product['id']}",
                use_container_width=True,
            )
 
        st.markdown("</div>", unsafe_allow_html=True)
 
    return clicked
 
 
def display_product_grid(products: List[Dict]) -> Optional[str]:
    """
    Shows products in a 3-column boutique grid.
    Returns product_id if a product was clicked, else None.
    """
    inject_css()
 
    if not products:
        st.info("No products available right now.")
        return None
 
    st.markdown('<p class="hs-eyebrow">Our collection</p>', unsafe_allow_html=True)
 
    clicked_id = None
    cols = st.columns(3, gap="medium")
 
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
    inject_css()
 
    st.button("← Back to collection", key="back_home")
 
    # Breadcrumb-style eyebrow
    st.markdown(
        f'<p class="hs-eyebrow">Collection / {product["name"]}</p>',
        unsafe_allow_html=True,
    )
    st.title(product["name"])
 
    img_col, info_col = st.columns([1, 1], gap="large")
 
    with img_col:
        try:
            image_path = os.path.join("assets", product["image"])
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.markdown(
                    '<div style="height:300px;background:#EFE8DC;border-radius:10px;'
                    'display:flex;align-items:center;justify-content:center;'
                    'color:#A0785A;">Image unavailable</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                '<div style="height:300px;background:#EFE8DC;border-radius:10px;'
                'display:flex;align-items:center;justify-content:center;'
                'color:#A0785A;">Image unavailable</div>',
                unsafe_allow_html=True,
            )
 
    with info_col:
        st.markdown(
            f'<p class="hs-price">${product["price"]:.2f}</p>',
            unsafe_allow_html=True,
        )
        st.write(product["description"])
        st.divider()
 
        qty = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)
 
        if st.button("Add to Cart", use_container_width=True, type="primary"):
            add_to_cart(cart, product["id"], int(qty))
            st.success(f"Added {int(qty)}× {product['name']} to your cart.")
 
# ---------------------------
# Review section UI
# ---------------------------

def display_reviews_section(product_id: str):
    """Shows recent reviews first, then the review form."""
    inject_css()

    st.divider()
    st.markdown('<p class="hs-eyebrow">Customer feedback</p>', unsafe_allow_html=True)
    st.subheader("Reviews")

    if "reviews" not in st.session_state:
        st.session_state.reviews = {}

    if product_id not in st.session_state.reviews:
        st.session_state.reviews[product_id] = []

    product_reviews = st.session_state.reviews.get(product_id, [])

    # Recent reviews first
    st.markdown("### Recent reviews")

    if not product_reviews:
        st.info("No reviews yet.")
    else:
        for review in reversed(product_reviews):
            verified_tag = "✅ Verified" if review["verified"] else "❌ Non-verified"
            stars = "⭐" * review["rating"]

            st.markdown(
                f"""
**{review['name']}** — {verified_tag}  
{stars}  
{review['text']}  

**Fit:** {review['fit']} | **Quality:** {review['quality']} | **Shipping:** {review['shipping']}
"""
            )
            st.divider()

    # Leave a review form second
    st.subheader("Leave a review")

    st.markdown("### Select rating")
    rating = st.slider("Rating", 1, 5, 5, key=f"rating_{product_id}")
    st.write("⭐" * rating)

    st.markdown("Tell others about your experience")
    review_text = st.text_area(
        "",
        key=f"review_text_{product_id}"
    )

    col1, col2 = st.columns(2)
    with col1:
        reviewer_name = st.text_input("Your name", key=f"name_{product_id}")
    with col2:
        reviewer_email = st.text_input("Your email", key=f"email_{product_id}")

    st.markdown("## Review details")
    d1, d2, d3 = st.columns(3)

    with d1:
        fit = st.selectbox(
            "Fit",
            ["Poor", "Okay", "Good", "Excellent"],
            key=f"fit_{product_id}"
        )

    with d2:
        quality = st.selectbox(
            "Quality",
            ["Poor", "Okay", "Good", "Excellent"],
            key=f"quality_{product_id}"
        )

    with d3:
        shipping = st.selectbox(
            "Shipping",
            ["Slow", "On time", "Fast"],
            key=f"shipping_{product_id}"
        )

    verified = st.checkbox("Verified purchase", key=f"verified_{product_id}")

    if st.button("Submit review", key=f"submit_review_{product_id}"):
        if review_text.strip() and reviewer_name.strip():
            st.session_state.reviews[product_id].append({
                "name": reviewer_name,
                "email": reviewer_email,
                "rating": rating,
                "text": review_text,
                "verified": verified,
                "fit": fit,
                "quality": quality,
                "shipping": shipping,
            })
            st.success("Review submitted!")
            st.rerun()
        else:
            st.warning("Please enter your name and your review before submitting.")

# ---------------------------
# Cart UI
# ---------------------------
 
def display_recent_activity(order_history):
    inject_css()
    st.markdown('<p class="hs-eyebrow">Recent purchases</p>', unsafe_allow_html=True)
    st.title("Recent Activity")
 
    if not order_history:
        st.info("No recent purchases yet.")
        return
 
    for order in order_history:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(order.get("item_name", "Order"))
                st.caption(f"Date: {order.get('date', '—')}")
                st.write("📍 Location: Store Pickup")
            with col2:
                price = order.get("calories_burned", 0.0)
                qty   = order.get("steps", 0)
                st.markdown(
                    f'<p class="hs-price">${price:.2f}</p>',
                    unsafe_allow_html=True,
                )
                st.caption(f"Qty: {qty}")
 
 
def display_cart_page(cart: Dict, products: List[Dict], user_id: str = "user1"):
    """
    Shows cart contents, totals, and checkout.
    Writes quantity changes back to BigQuery via data_fetcher helpers.
    """
    inject_css()
 
    if "order_history" not in st.session_state:
        st.session_state.order_history = []
 
    from data_fetcher import upsert_cart_item, delete_cart_item, clear_cart
 
    st.markdown('<p class="hs-eyebrow">Review your order</p>', unsafe_allow_html=True)
    st.title("Your Cart")
 
    if st.session_state.get("checkout_success_msg"):
        st.success(st.session_state.checkout_success_msg)
        st.session_state.checkout_success_msg = None
 
    if not cart:
        st.info("Your cart is empty — head back to the collection to add some hats.")
        return
 
    # ── Line items ──
    for product_id, qty in list(cart.items()):
        product = get_product_by_id(products, product_id)
        if not product:
            continue
 
        with st.container(border=True):
            cols = st.columns([1, 3, 1, 1], gap="small")
 
            with cols[0]:
                try:
                    st.image(product["image"], use_container_width=True)
                except Exception:
                    st.markdown(
                        '<div style="height:64px;background:#EFE8DC;border-radius:8px;"></div>',
                        unsafe_allow_html=True,
                    )
 
            with cols[1]:
                st.markdown(
                    f'<p class="hs-cart-name">{product["name"]}</p>'
                    f'<p class="hs-cart-sub">${product["price"]:.2f} each</p>'
                    f'<p class="hs-cart-sub">Subtotal: <strong>${product["price"] * qty:.2f}</strong></p>',
                    unsafe_allow_html=True,
                )
 
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
                    upsert_cart_item(user_id, product_id, int(new_qty))
                    st.rerun()
 
            with cols[3]:
                if st.button("Remove", key=f"rm_{product_id}"):
                    remove_from_cart(cart, product_id)
                    delete_cart_item(user_id, product_id)
                    st.rerun()
 
    # ── Total + checkout ──
    st.divider()
    total = calc_total(cart, products)
 
    total_col, btn_col = st.columns([2, 1])
    with total_col:
        st.markdown(
            f'<p class="hs-cart-sub" style="margin-bottom:2px;">Order total</p>'
            f'<p class="hs-price" style="font-size:28px;">${total:.2f}</p>',
            unsafe_allow_html=True,
        )
    with btn_col:
        if st.button("Proceed to Checkout", use_container_width=True, type="primary"):
            total_val = calc_total(cart, products)
            total_qty, _ = count_cart_items(cart)
 
            import datetime
            new_order = {
                "item_name": "Hat Order",
                "date": datetime.date.today().isoformat(),
                "calories_burned": total_val,
                "steps": total_qty,
            }
            st.session_state.order_history.append(new_order)
 
            msg = checkout_message(cart, products)
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
    inject_css()
 
    st.markdown('<p class="hs-eyebrow">Your history</p>', unsafe_allow_html=True)
    st.title("Orders")
 
    if not orders:
        st.info("You haven't placed any orders yet.")
        return
 
    product_lookup = {p["id"]: p for p in products}
 
    for order in orders:
        with st.container(border=True):
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
                st.markdown(
                    f'<p class="hs-order-id">Order #{order_id}</p>',
                    unsafe_allow_html=True,
                )
                st.caption(f"📅 {order_date}")
 
                if product_id and str(product_id) in product_lookup:
                    product = product_lookup[str(product_id)]
                    st.write(f"🧢 **{product['name']}**")
                    try:
                        st.image(product["image"], width=80)
                    except Exception:
                        pass
                elif product_id:
                    st.write(f"Product ID: `{product_id}`")
 
                if quantity is not None:
                    st.caption(f"Qty: {quantity}")
 
                if status:
                    status_map = {
                        "delivered":  "✅ Delivered",
                        "shipped":    "🚚 Shipped",
                        "processing": "⏳ Processing",
                        "cancelled":  "❌ Cancelled",
                    }
                    label = status_map.get(str(status).lower(), f"📋 {status}")
                    st.write(label)
 
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

    if timestamp:
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
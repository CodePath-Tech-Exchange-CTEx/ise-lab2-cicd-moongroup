#############################################################################
# catalog_filter.py
#
# Filterable hat catalog page driven by real BigQuery product schema:
#   product_id, name, price, description, image_url, stock, color, style
#
# Usage in app.py:
#   from catalog_filter import display_catalog_filter
#   clicked_id = display_catalog_filter(products, st.session_state.cart)
#   if clicked_id:
#       st.session_state.selected_product = clicked_id
#       st.rerun()
#############################################################################

import os
import streamlit as st
from typing import Dict, List, Optional
from modules import add_to_cart, inject_css


# ---------------------------------------------------------------------------
# Color → hex mapping for swatch strips
# Extend this dict as new colors are added to BigQuery
# ---------------------------------------------------------------------------

COLOR_HEX = {
    "black":  "#1a1a1a",
    "blue":   "#1b2a4a",
    "red":    "#B03020",
    "green":  "#3B6D11",
    "beige":  "#C8A882",
    "brown":  "#6B3E1E",
    "white":  "#F5F0E8",
    "grey":   "#888780",
    "gray":   "#888780",
    "navy":   "#162444",
    "yellow": "#C89A10",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _meta(products: List[Dict]) -> tuple:
    """Extract distinct filter values and price/stock bounds from the product list."""
    colors = sorted({p.get("color", "").strip().title() for p in products if p.get("color")})
    styles = sorted({p.get("style", "").strip().title() for p in products if p.get("style")})
    prices = [p["price"] for p in products if isinstance(p.get("price"), (int, float))]
    stocks = [p["stock"] for p in products if isinstance(p.get("stock"), (int, float))]
    min_p  = int(min(prices)) if prices else 0
    max_p  = int(max(prices)) if prices else 500
    max_s  = int(max(stocks)) if stocks else 100
    return colors, styles, min_p, max_p, max_s


def _filter(
    products:      List[Dict],
    price_range:   tuple,
    min_stock:     int,
    hide_oos:      bool,
    chosen_colors: List[str],
    chosen_styles: List[str],
    sort_by:       str,
) -> List[Dict]:
    lo, hi = price_range
    out = []
    for p in products:
        price = p.get("price", 0)
        stock = p.get("stock", 0)
        color = p.get("color", "").strip().title()
        style = p.get("style", "").strip().title()

        if not (lo <= price <= hi):
            continue
        if hide_oos and stock == 0:
            continue
        if stock < min_stock:
            continue
        if chosen_colors and color not in chosen_colors:
            continue
        if chosen_styles and style not in chosen_styles:
            continue
        out.append(p)

    if sort_by == "Price: low to high":
        out.sort(key=lambda p: p.get("price", 0))
    elif sort_by == "Price: high to low":
        out.sort(key=lambda p: p.get("price", 0), reverse=True)
    elif sort_by == "Stock: most first":
        out.sort(key=lambda p: p.get("stock", 0), reverse=True)
    elif sort_by == "Name A-Z":
        out.sort(key=lambda p: p.get("name", "").lower())

    return out


def _stock_badge(stock: int) -> str:
    """Returns an inline HTML badge based on stock level."""
    if stock == 0:
        return (
            '<span style="background:#FCEBEB;color:#A32D2D;font-size:10px;'
            'padding:2px 8px;border-radius:4px;letter-spacing:0.06em;">'
            'Out of stock</span>'
        )
    if stock <= 5:
        return (
            f'<span style="background:#FAEEDA;color:#854F0B;font-size:10px;'
            f'padding:2px 8px;border-radius:4px;letter-spacing:0.06em;">'
            f'Only {stock} left</span>'
        )
    return (
        f'<span style="background:#EAF3DE;color:#3B6D11;font-size:10px;'
        f'padding:2px 8px;border-radius:4px;letter-spacing:0.06em;">'
        f'{stock} in stock</span>'
    )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def display_catalog_filter(products: List[Dict], cart: Dict) -> Optional[str]:
    """
    Full filterable catalog page using the BigQuery product schema.

    Sidebar:  price range, color checkboxes, style checkboxes,
              min-stock slider, hide-out-of-stock toggle, clear button.
    Main:     sort dropdown, result count, 3-column product grid with
              color strip, stock badge, style tag, add-to-cart + details.

    Returns product_id string if "Details" was clicked, else None.
    """
    inject_css()

    if not products:
        st.info("No products found.")
        return None

    colors, styles, min_p, max_p, max_s = _meta(products)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<p style="font-size:10px;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#7B5B3A;margin-bottom:0.75rem;">'
            'Refine your search</p>',
            unsafe_allow_html=True,
        )

        # Price range
        st.markdown("**Price**")
        price_range = st.slider(
            "Price range",
            min_value=min_p,
            max_value=max_p if max_p > min_p else min_p + 1,
            value=(min_p, max_p if max_p > min_p else min_p + 1),
            format="$%d",
            label_visibility="collapsed",
        )
        st.markdown(" ")

        # Color
        if colors:
            st.markdown("**Color**")
            chosen_colors = []
            for color in colors:
                hex_val = COLOR_HEX.get(color.lower(), "#888")
                label   = (
                    f'<span style="display:inline-block;width:10px;height:10px;'
                    f'background:{hex_val};border-radius:50%;margin-right:6px;'
                    f'border:0.5px solid #C8B89A;vertical-align:middle;"></span>{color}'
                )
                if st.checkbox(color, key=f"color_{color}"):
                    chosen_colors.append(color)
        else:
            chosen_colors = []

        st.markdown(" ")

        # Style
        if styles:
            st.markdown("**Style**")
            chosen_styles = []
            for style in styles:
                if st.checkbox(style, key=f"style_{style}"):
                    chosen_styles.append(style)
        else:
            chosen_styles = []

        st.markdown(" ")

        # Stock
        st.markdown("**Stock**")
        hide_oos  = st.toggle("Hide out-of-stock", value=False)
        min_stock = st.slider(
            "Min. units in stock",
            min_value=0,
            max_value=max(max_s, 1),
            value=0,
            step=1,
        )

        st.divider()

        if st.button("Clear all filters", use_container_width=True):
            for k in [k for k in st.session_state if k.startswith(("color_", "style_"))]:
                del st.session_state[k]
            st.rerun()

    # ── Main area ─────────────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;'
        'color:#7B5B3A;margin-bottom:0.25rem;">Our collection</p>',
        unsafe_allow_html=True,
    )

    head_l, head_r = st.columns([3, 1])

    with head_r:
        sort_by = st.selectbox(
            "Sort",
            options=["Featured", "Price: low to high", "Price: high to low",
                     "Stock: most first", "Name A-Z"],
            label_visibility="collapsed",
        )

    filtered = _filter(
        products, price_range, min_stock, hide_oos,
        chosen_colors, chosen_styles, sort_by,
    )

    with head_l:
        st.markdown(
            f'Showing <span style="color:#7B4F2E;font-weight:600;">{len(filtered)}</span>'
            f' of {len(products)} hats',
            unsafe_allow_html=True,
        )

    if not filtered:
        st.warning("No hats match your current filters — try widening the price range or clearing a filter.")
        return None

    # ── Product grid ──────────────────────────────────────────────────────────
    clicked_id = None
    cols = st.columns(3, gap="medium")

    for idx, product in enumerate(filtered):
        pid   = str(product.get("product_id") or product.get("id", ""))
        name  = product.get("name", "Unnamed hat")
        price = product.get("price", 0)
        desc  = product.get("description", "")
        img   = product.get("image_url") or product.get("image", "")
        stock = int(product.get("stock", 0))
        color = product.get("color", "").strip()
        style = product.get("style", "").strip()
        hex_c = COLOR_HEX.get(color.lower(), "#C8B89A")

        with cols[idx % 3]:

            # Colored top strip
            st.markdown(
                f'<div style="height:5px;background:{hex_c};'
                f'border-radius:4px 4px 0 0;margin-bottom:4px;"></div>',
                unsafe_allow_html=True,
            )

            # Image — resolve assets/ folder first, fall back to raw URL
            img_displayed = False
            if img:
                assets_path = os.path.join("assets", img)
                if os.path.exists(assets_path):
                    st.image(assets_path, use_container_width=True)
                    img_displayed = True
                elif img.startswith(("http://", "https://")):
                    try:
                        st.image(img, use_container_width=True)
                        img_displayed = True
                    except Exception:
                        pass
            if not img_displayed:
                st.markdown(
                    '<div style="height:150px;background:#EFE8DC;border-radius:8px;'
                    'display:flex;align-items:center;justify-content:center;'
                    'font-size:12px;color:#A0785A;">No image</div>',
                    unsafe_allow_html=True,
                )

            # Style tag + stock badge
            style_tag = (
                f'<span style="font-size:10px;background:#EFE8DC;color:#7B4F2E;'
                f'padding:2px 8px;border-radius:4px;letter-spacing:0.06em;">'
                f'{style}</span>' if style else ""
            )
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;margin:6px 0 4px;">'
                f'{style_tag}{_stock_badge(stock)}</div>',
                unsafe_allow_html=True,
            )

            # Name + price
            st.markdown(
                f'<p style="font-size:14px;font-weight:600;color:#2C1A0E;margin:0 0 2px;">'
                f'{name}</p>'
                f'<p style="font-size:18px;font-weight:600;color:#5C3318;margin:0 0 6px;">'
                f'${price:.2f}</p>',
                unsafe_allow_html=True,
            )

            # Description snippet
            if desc:
                st.caption(desc[:80] + ("…" if len(desc) > 80 else ""))

            # Action buttons
            btn_l, btn_r = st.columns(2)
            with btn_l:
                if st.button(
                    "Add to cart",
                    key=f"cf_add_{pid}_{idx}",
                    use_container_width=True,
                    disabled=(stock == 0),
                ):
                    add_to_cart(cart, pid, 1)
                    try:
                        from data_fetcher import upsert_cart_item
                        upsert_cart_item("user1", pid, cart[pid])
                    except Exception as e:
                        st.warning(f"Cart saved locally but not synced: {e}")
                    st.toast(f"Added {name} to cart!")
            with btn_r:
                if st.button(
                    "Details",
                    key=f"cf_view_{pid}_{idx}",
                    use_container_width=True,
                ):
                    clicked_id = pid

            st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)

    return clicked_id
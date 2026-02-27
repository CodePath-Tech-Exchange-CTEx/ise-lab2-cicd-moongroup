#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component


# This one has been written for you as an example. You may change it as wanted.
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


# ---------------------------
# Product Data
# ---------------------------

from typing import List, Dict, Optional, Any


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


def get_product_by_id(products: List[Dict[str, Any]], product_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a single product dict by its id, or None if not found.
    """
    for product in products:
        if product.get("id") == product_id:
            return product
    return None
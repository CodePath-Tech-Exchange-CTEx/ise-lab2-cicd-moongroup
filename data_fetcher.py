#############################################################################
# data_fetcher.py
#
# Cleaned + fixed BigQuery backend for HatPlug app
#############################################################################

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import os
import json

# ==============================
# CONFIG
# ==============================
PROJECT_ID = os.getenv("PROJECT_ID", "oluwadunsin-adesanya-fisk")
DATASET = "hatplugquery"
LOCATION = "us-central1"

# ==============================
# CLIENTS
# ==============================
try:
    bq_client = bigquery.Client(project=PROJECT_ID)
except Exception as e:
    print(f"BigQuery Init Error: {e}")
    bq_client = None

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    genai_model = GenerativeModel("gemini-2.5-flash-lite")
except Exception as e:
    print(f"Vertex AI Init Error: {e}")
    genai_model = None

# ==============================
# RUN QUERY HELPER
# ==============================
def run_query(query, params=None):
    if bq_client is None:
        return []

    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    results = bq_client.query(query, job_config=job_config).result()

    return [dict(row) for row in results]

# ==============================
# PRODUCTS
# ==============================
def get_products():
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.products`
        LIMIT 100
    """
    return run_query(query)


def get_product(product_id):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.products`
        WHERE product_id = @product_id
        LIMIT 1
    """
    params = [
        bigquery.ScalarQueryParameter("product_id", "STRING", product_id)
    ]
    result = run_query(query, params)
    return result[0] if result else None

# ==============================
# USERS
# ==============================
def get_user(user_id):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.users`
        WHERE user_id = @user_id
        LIMIT 1
    """
    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    result = run_query(query, params)
    return result[0] if result else None

# ==============================
# CART
# ==============================
def get_cart(user_id):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.cart`
        WHERE user_id = @user_id
    """
    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    return run_query(query, params)


def upsert_cart_item(user_id, product_id, quantity):
    query = f"""
    MERGE `{PROJECT_ID}.{DATASET}.cart` T
    USING (
        SELECT
            @user_id AS user_id,
            @product_id AS product_id,
            @quantity AS quantity
    ) S
    ON T.user_id = S.user_id AND T.product_id = S.product_id

    WHEN MATCHED THEN
        UPDATE SET quantity = S.quantity

    WHEN NOT MATCHED THEN
        INSERT (user_id, product_id, quantity)
        VALUES (S.user_id, S.product_id, S.quantity)
    """

    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("product_id", "STRING", str(product_id)),
        bigquery.ScalarQueryParameter("quantity", "INT64", quantity),
    ]

    return run_query(query, params)


def delete_cart_item(user_id, product_id):
    query = f"""
    DELETE FROM `{PROJECT_ID}.{DATASET}.cart`
    WHERE user_id = @user_id
    AND product_id = @product_id
    """

    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("product_id", "STRING", str(product_id)),
    ]

    return run_query(query, params)


def clear_cart(user_id):
    query = f"""
    DELETE FROM `{PROJECT_ID}.{DATASET}.cart`
    WHERE user_id = @user_id
    """

    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
    ]

    return run_query(query, params)

# ==============================
# ORDERS (FIXED)
# ==============================
def get_orders(user_id):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.orders`
        WHERE user_id = @user_id
        ORDER BY COALESCE(order_date, CURRENT_TIMESTAMP()) DESC
    """
    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    return run_query(query, params)


def create_order(user_id, product_id, quantity):
    query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET}.orders`
        (user_id, product_id, quantity, order_date)
        VALUES (@user_id, @product_id, @quantity, CURRENT_TIMESTAMP())
    """

    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("product_id", "STRING", str(product_id)),
        bigquery.ScalarQueryParameter("quantity", "INT64", quantity),
    ]

    return run_query(query, params)

# ==============================
# AI RECOMMENDATIONS
# ==============================
def get_genai_recommendations(user_id, cart_items=None):
    cart = cart_items if cart_items is not None else get_cart(user_id)
    orders = get_orders(user_id)

    prompt = f"""
    You are a fashion stylist specializing in hats.

    The user currently has these hats in their cart:
    {cart}

    They have previously ordered these hats:
    {orders}

    Give personalised style advice ONLY based on the hats above.
    Do not recommend new hats to buy. Instead:
    - Suggest outfits, occasions, or looks that suit the hats they already own or are buying
    - Point out how their hats can be mixed and matched
    - Give one specific tip per hat if possible

    Keep the tone friendly, confident, and concise.
    If the cart and order history are both empty, politely tell the user to add some hats first before asking for style advice.
    """

    if genai_model is None:
        return {"user_id": user_id, "recommendations": []}

    response = genai_model.generate_content(prompt)

    try:
        recommendations = json.loads(response.text)
    except:
        recommendations = response.text  

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

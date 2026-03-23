#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import os

PROJECT_ID=os.getenv("oluwadunsin-adesanya-fisk")
DATASET="hat_plug"
LOCATION="us-central1"
 
bq_client=bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=LOCATION)
genai_model=GenerativeModel("gemini-1.5-flash")
 
# ==============================
# HELPER FUNCTION
# ==============================
def run_query(query, params=None):
    """Executes a query and returns clean results."""
    job_config=bigquery.QueryJobConfig(query_parameters=params or [])
    query_job=bq_client.query(query, job_config=job_config)
    results=query_job.result()
    rows=[]
    for row in results:
        rows.append(dict(row))
    return rows
 
# ==============================
# HATS:)
# ==============================
def get_products():
    query=f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.products`
        LIMIT 100
    """
    return run_query(query)
 
def get_product(product_id):
    query=f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.products`
        WHERE product_id = @product_id
        LIMIT 1
    """
    params=[
        bigquery.ScalarQueryParameter("product_id", "STRING", product_id)
    ]
    results=run_query(query, params)
    return results[0] if results else None
 
# ==============================
# WEB-USERS
# ==============================
def get_user(user_id):
    query=f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.users`
        WHERE user_id = @user_id
        LIMIT 1
    """
    params=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    results=run_query(query, params)
    return results[0] if results else None
 
# ==============================
# CART!
# ==============================
def get_cart(user_id):
    query=f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.cart`
        WHERE user_id = @user_id
    """
    params=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    return run_query(query, params)
 
# ==============================
# ORDERS!
# ==============================
def get_orders(user_id):
    query=f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.orders`
        WHERE user_id = @user_id
        ORDER BY order_date DESC
    """
    params=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    return run_query(query, params)
 
# ==============================
# AI RECOMMENDATIONS(OPTIONAL)
# ==============================
def get_genai_recommendations(user_id):
    """
    Returns AI-generated hat recommendations
    """
    cart=get_cart(user_id)
    orders=get_orders(user_id)
    prompt=f"""
    You are a fashion stylist specializing in hats.
    Based on:
    Cart: {cart}
    Previous Orders: {orders}
    Recommend 3 hats the user would like.
    Return JSON with:
    - product_name
    - style (e.g., streetwear, luxury, sporty)
    - reason
    """
    response=genai_model.generate_content(prompt)
    return {
        "user_id": user_id,
        "recommendations": response.text
    }
 

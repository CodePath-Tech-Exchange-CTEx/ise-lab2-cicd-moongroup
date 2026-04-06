#############################################################################
# data_fetcher.py
#############################################################################

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import os
import json

# FIX: os.getenv looks for the KEY name. 
# We'll default to your project ID if the environment variable isn't set.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "oluwadunsin-adesanya-fisk")
DATASET = "hat_plug"
LOCATION = "us-central1"

# Initialize Clients
try:
    bq_client = bigquery.Client(project=PROJECT_ID)
except Exception as e:
    print(f"BigQuery Init Error: {e}")
    bq_client = None

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    # 1.5 Flash is great for speed and JSON tasks
    genai_model = GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Vertex AI Init Error: {e}")
    genai_model = None

# ==============================
# HELPER FUNCTION
# ==============================
def run_query(query, params=None):
    """Executes a query and returns clean results."""
    if bq_client is None:
        return []

    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    try:
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Query Error: {e}")
        return []

# ==============================
# HATS:)
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
    results = run_query(query, params)
    return results[0] if results else None

# ==============================
# WEB-USERS
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
    results = run_query(query, params)
    return results[0] if results else None

# ==============================
# CART!
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

# ==============================
# ORDERS!
# ==============================
def get_orders(user_id):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.orders`
        WHERE user_id = @user_id
        ORDER BY order_date DESC
    """
    params = [
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
    ]
    return run_query(query, params)

# ==============================
# AI RECOMMENDATIONS
# ==============================
def get_genai_recommendations(user_id):
    """
    Returns AI-generated hat recommendations as a structured list.
    """
    cart = get_cart(user_id)
    orders = get_orders(user_id)
    
    if not cart and not orders:
        return {"user_id": user_id, "recommendations": [], "message": "No history found."}

    prompt = f"""
    You are a fashion stylist specializing in hats.
    Based on the following user data:
    Cart: {cart}
    Previous Orders: {orders}
    
    Recommend 3 hats the user would like. 
    Return a JSON list of objects. Each object must have:
    - product_name
    - style
    - reason
    """
    
    if genai_model is None:
        return {"user_id": user_id, "recommendations": "AI Service Offline"}

    try:
        # Using GenerationConfig ensures the model strictly returns valid JSON
        response = genai_model.generate_content(
            prompt,
            generation_config=GenerationConfig(response_mime_type="application/json")
        )
        
        # Load the string response into a Python list
        recommendations_data = json.loads(response.text)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations_data
        }
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return {"user_id": user_id, "recommendations": [], "error": str(e)}

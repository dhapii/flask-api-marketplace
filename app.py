from flask import Flask, jsonify, request
from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# --- Routes ---
@app.route("/")
def index():
    return {"message": "API is running!"}

@app.route("/products", methods=["GET"])
def get_products():
    category = request.args.get("category")  # optional filter
    query = supabase.table("products").select("*")
    if category:
        query = query.eq("category", category)
    data = query.execute()
    return jsonify(data.data)

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    data = supabase.table("products").select("*").eq("id", product_id).single().execute()
    if not data.data:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(data.data)

@app.route("/products", methods=["POST"])
def create_product():
    new_product = request.json
    data = supabase.table("products").insert(new_product).execute()
    return jsonify(data.data), 201

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    update_data = request.json
    data = supabase.table("products").update(update_data).eq("id", product_id).execute()
    return jsonify(data.data)

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    supabase.table("products").delete().eq("id", product_id).execute()
    return jsonify({"message": f"Product {product_id} deleted"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

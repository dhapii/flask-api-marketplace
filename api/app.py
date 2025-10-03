from flask import Flask, jsonify, request
from supabase import create_client
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# =========================================================
# Helpers: cek role user
# =========================================================
def get_user_role(username):
    res = supabase.table("users").select("role").eq("username", username).single().execute()
    if res.data:
        return res.data["role"]
    return None

def require_admin(f):
    def wrapper(*args, **kwargs):
        username = request.headers.get("X-User")
        if not username:
            return jsonify({"error": "Missing X-User header"}), 401
        role = get_user_role(username)
        if role != "admin":
            return jsonify({"error": "Only admin can perform this action"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def require_login(f):
    def wrapper(*args, **kwargs):
        username = request.headers.get("X-User")
        if not username:
            return jsonify({"error": "Missing X-User header"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# =========================================================
# Routes
# =========================================================
@app.route("/")
def index():
    return {"message": "API is running on Vercel"}

# =========================================================
# PRODUCTS (CRUD hanya admin)
# =========================================================
@app.route("/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
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
@require_admin
def create_product():
    new_product = request.json
    data = supabase.table("products").insert(new_product).execute()
    return jsonify(data.data), 201

@app.route("/products/<int:product_id>", methods=["PUT"])
@require_admin
def update_product(product_id):
    update_data = request.json
    data = supabase.table("products").update(update_data).eq("id", product_id).execute()
    return jsonify(data.data)

@app.route("/products/<int:product_id>", methods=["DELETE"])
@require_admin
def delete_product(product_id):
    supabase.table("products").delete().eq("id", product_id).execute()
    return jsonify({"message": f"Product {product_id} deleted"})

# =========================================================
# FORUMS
# =========================================================
@app.route("/forums", methods=["GET"])
def get_forums():
    data = supabase.table("forums").select("*").execute()
    return jsonify(data.data)

@app.route("/forums", methods=["POST"])
@require_admin
def create_forum():
    new_forum = request.json
    data = supabase.table("forums").insert(new_forum).execute()
    return jsonify(data.data), 201

# =========================================================
# THREADS
# =========================================================
@app.route("/threads/<int:forum_id>", methods=["GET"])
def get_threads(forum_id):
    data = supabase.table("threads").select("*").eq("forum_id", forum_id).execute()
    return jsonify(data.data)

@app.route("/threads", methods=["POST"])
@require_login
def create_thread():
    username = request.headers.get("X-User")
    user = supabase.table("users").select("id").eq("username", username).single().execute()
    if not user.data:
        return jsonify({"error": "User not found"}), 404

    new_thread = request.json
    new_thread["user_id"] = user.data["id"]
    data = supabase.table("threads").insert(new_thread).execute()
    return jsonify(data.data), 201

# =========================================================
# POSTS (komentar di thread)
# =========================================================
@app.route("/posts/<int:thread_id>", methods=["GET"])
def get_posts(thread_id):
    data = supabase.table("posts").select("*").eq("thread_id", thread_id).execute()
    return jsonify(data.data)

@app.route("/posts", methods=["POST"])
@require_login
def create_post():
    username = request.headers.get("X-User")
    user = supabase.table("users").select("id").eq("username", username).single().execute()
    if not user.data:
        return jsonify({"error": "User not found"}), 404

    new_post = request.json
    new_post["user_id"] = user.data["id"]
    data = supabase.table("posts").insert(new_post).execute()
    return jsonify(data.data), 201

# =========================================================
# HANDLER UNTUK VERCEL
# =========================================================
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)

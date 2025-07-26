from flask import Blueprint, request, jsonify
import random
import pandas as pd

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.record
def record_params(setup_state):
    # MongoDB vendors collection passed from app.py
    global vendors_collection
    vendors_collection = setup_state.options["vendors"]

    # Load CSV once at start
    global dish_df
    dish_df = pd.read_csv("C:/Users/LENOVO/Downloads/IndianFoodDataset.csv.zip")

# Default language
language = "english"

# --- Set Language ---
@chatbot_bp.route("/language", methods=["POST"])
def set_language():
    global language
    data = request.json
    language = data.get("language", "english")
    return jsonify({"message": "Language set successfully", "language": language})

# --- Fetch Vendors from MongoDB ---
@chatbot_bp.route("/vendors", methods=["GET"])
def get_vendors():
    vendors = list(vendors_collection.find({}, {"_id": 0}))
    if len(vendors) == 0:
        return jsonify({"vendors": []})
    selected = random.sample(vendors, min(4, len(vendors)))
    return jsonify({"vendors": selected})

# --- Fetch Dish Ingredients from CSV ---
@chatbot_bp.route("/ingredients", methods=["POST"])
def get_ingredients():
    dish_name = request.json.get("dish", "").strip().lower()

    # Search exact match first
    result = dish_df[dish_df['dish'].str.lower() == dish_name]

    # If not exact match, try partial match
    if result.empty:
        result = dish_df[dish_df['dish'].str.lower().str.contains(dish_name)]

    if not result.empty:
        ingredients = result.iloc[0]['ingredients']
        # Hinglish translation if selected
        if language == "hinglish":
            return jsonify({"ingredients": [f"{ing.strip()} (samagri)" for ing in ingredients.split(",")]})
        else:
            return jsonify({"ingredients": [ing.strip() for ing in ingredients.split(",")]})
    else:
        return jsonify({"error": "Dish not found"}), 404

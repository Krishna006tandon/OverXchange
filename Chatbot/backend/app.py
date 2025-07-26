from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from chatbot_routes import chatbot_bp

app = Flask(__name__)
CORS(app)

# ===== MongoDB Atlas Connection =====
MONGO_URI = "mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["streetfood_db"]        # same DB used by vendor registration
vendors_collection = db["vendors"]  # live vendor data

# Register chatbot blueprint with vendors collection
app.register_blueprint(
    chatbot_bp,
    url_prefix="/chat",
    vendors=vendors_collection
)

@app.route('/')
def home():
    return "Chatbot Backend Running with MongoDB + CSV"

if __name__ == "__main__":
    app.run(debug=True)

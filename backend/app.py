from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

@app.route('/')
def home():
    return 'Welcome to OverXchange Backend!'

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Dummy logic: just echo back
    return jsonify({"success": True, "message": "Login successful (dummy)", "data": data})

@app.route('/api/signup/vendor', methods=['POST'])
def signup_vendor():
    data = request.json
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])
    result = db['vendors'].insert_one(data)
    return jsonify({"success": True, "message": "Vendor signup successful!", "id": str(result.inserted_id)})

@app.route('/api/signup/supplier', methods=['POST'])
def signup_supplier():
    data = request.json
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])
    result = db['suppliers'].insert_one(data)
    return jsonify({"success": True, "message": "Supplier signup successful!", "id": str(result.inserted_id)})

if __name__ == '__main__':
    app.run(debug=True) 
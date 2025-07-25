from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson import ObjectId
from flask import abort
from werkzeug.security import check_password_hash

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
    username = data.get('username')
    password = data.get('password')
    # Try vendor first
    user = db['vendors'].find_one({'email': username})
    user_type = 'vendor'
    if not user:
        user = db['suppliers'].find_one({'email': username})
        user_type = 'supplier' if user else None
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'Incorrect password'}), 401
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user_type': user_type,
        'user_id': str(user['_id'])
    })

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

def get_user_collection(user_type):
    if user_type == 'vendor':
        return db['vendors']
    elif user_type == 'supplier':
        return db['suppliers']
    else:
        abort(400, 'Invalid user type')

@app.route('/api/profile/<user_type>/<user_id>', methods=['GET'])
def get_profile(user_type, user_id):
    collection = get_user_collection(user_type)
    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        abort(404, 'User not found')
    user.pop('password', None)  # Never send password
    user['user_type'] = user_type
    user['user_id'] = str(user['_id'])
    user['_id'] = str(user['_id'])
    return jsonify(user)

@app.route('/api/profile/<user_type>/<user_id>', methods=['PUT'])
def update_profile(user_type, user_id):
    collection = get_user_collection(user_type)
    data = request.json
    update_fields = {k: v for k, v in data.items() if k in ['name', 'email', 'bio', 'shop_name', 'company_name']}
    result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_fields})
    if result.matched_count == 0:
        abort(404, 'User not found')
    return jsonify({'success': True, 'message': 'Profile updated!'})

if __name__ == '__main__':
    app.run(debug=True) 
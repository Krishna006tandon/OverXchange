from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson import ObjectId
from flask import abort
from werkzeug.security import check_password_hash
from datetime import datetime

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

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers for vendor order form"""
    suppliers = list(db['suppliers'].find({}, {'password': 0}))  # Exclude password
    for supplier in suppliers:
        supplier['_id'] = str(supplier['_id'])
    return jsonify({'success': True, 'suppliers': suppliers})

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get all stocks"""
    stocks = list(db['stocks'].find({}))
    for stock in stocks:
        stock['_id'] = str(stock['_id'])
        stock['supplier_id'] = str(stock['supplier_id'])
    return jsonify({'success': True, 'stocks': stocks})

@app.route('/api/stocks/supplier/<supplier_id>', methods=['GET'])
def get_supplier_stocks(supplier_id):
    """Get stocks for a specific supplier"""
    stocks = list(db['stocks'].find({'supplier_id': supplier_id}))
    for stock in stocks:
        stock['_id'] = str(stock['_id'])
        stock['supplier_id'] = str(stock['supplier_id'])
    return jsonify({'success': True, 'stocks': stocks})

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """Add a new stock item"""
    data = request.json
    data['created_at'] = datetime.now()
    data['updated_at'] = datetime.now()
    result = db['stocks'].insert_one(data)
    return jsonify({'success': True, 'message': 'Stock added successfully!', 'id': str(result.inserted_id)})

@app.route('/api/stocks/<stock_id>', methods=['PUT'])
def update_stock(stock_id):
    """Update a stock item"""
    data = request.json
    data['updated_at'] = datetime.now()
    result = db['stocks'].update_one({'_id': ObjectId(stock_id)}, {'$set': data})
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Stock not found'}), 404
    return jsonify({'success': True, 'message': 'Stock updated successfully!'})

@app.route('/api/stocks/<stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """Delete a stock item"""
    result = db['stocks'].delete_one({'_id': ObjectId(stock_id)})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Stock not found'}), 404
    return jsonify({'success': True, 'message': 'Stock deleted successfully!'})

@app.route('/api/dashboard/<supplier_id>', methods=['GET'])
def get_dashboard_data(supplier_id):
    """Get dashboard analytics for a supplier"""
    try:
        # Get all stocks for the supplier
        stocks = list(db['stocks'].find({'supplier_id': supplier_id}))
        
        # Calculate analytics
        total_products = len(stocks)
        low_stock_items = len([s for s in stocks if s['quantity_available'] > 0 and s['quantity_available'] <= 10])
        out_of_stock_items = len([s for s in stocks if s['quantity_available'] == 0])
        total_value = sum(s['quantity_available'] * s['price_per_unit'] for s in stocks)
        
        # Get recent stocks (last 5 updated)
        recent_stocks = sorted(stocks, key=lambda x: x['updated_at'], reverse=True)[:5]
        
        # Category distribution
        category_counts = {}
        for stock in stocks:
            category = stock['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Convert ObjectId to string for JSON serialization
        for stock in recent_stocks:
            stock['_id'] = str(stock['_id'])
            stock['supplier_id'] = str(stock['supplier_id'])
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_products': total_products,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'total_value': total_value,
                'category_distribution': category_counts
            },
            'recent_stocks': recent_stocks
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
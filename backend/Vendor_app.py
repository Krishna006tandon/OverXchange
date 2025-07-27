from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import json
import bcrypt
import jwt
from functools import wraps
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['vendornet']

# Collections
users = db['users']
listings = db['listings']
transactions = db['transactions']
chats = db['chats']
feedback = db['feedback']
analytics = db['analytics']

# JWT Token Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes

@app.route('/')
def index():
    return render_template('vendornet.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if users.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user = {
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'company': data.get('company', ''),
        'location': data.get('location', ''),
        'phone': data.get('phone', ''),
        'trust_score': 5.0,
        'total_transactions': 0,
        'created_at': datetime.utcnow()
    }
    
    result = users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    del user['password']
    
    return jsonify({'message': 'User registered successfully', 'user': user}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = users.find_one({'email': data['email']})
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': str(user['_id']),
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['JWT_SECRET_KEY'])
    
    user['_id'] = str(user['_id'])
    del user['password']
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user
    })

@app.route('/api/listings', methods=['GET'])
def get_listings():
    # Get filter parameters
    product = request.args.get('product', '').lower()
    city = request.args.get('city', '').lower()
    pincode = request.args.get('pincode', '')
    listing_type = request.args.get('type', '')
    
    # Build filter query
    filter_query = {}
    if product:
        filter_query['product'] = {'$regex': product, '$options': 'i'}
    if city:
        filter_query['city'] = {'$regex': city, '$options': 'i'}
    if pincode:
        filter_query['pincode'] = {'$regex': pincode, '$options': 'i'}
    if listing_type:
        filter_query['type'] = listing_type
    
    # Get listings with user details
    listings_data = []
    for listing in listings.find(filter_query).sort('created_at', -1):
        listing['_id'] = str(listing['_id'])
        listing['user_id'] = str(listing['user_id'])
        
        # Get user details
        user = users.find_one({'_id': ObjectId(listing['user_id'])})
        if user:
            listing['vendor_name'] = user['name']
            listing['vendor_trust_score'] = user['trust_score']
        
        listings_data.append(listing)
    
    return jsonify({'listings': listings_data})

@app.route('/api/listings', methods=['POST'])
@token_required
def create_listing(current_user):
    data = request.get_json()
    
    listing = {
        'user_id': ObjectId(current_user['_id']),
        'type': data['type'],  # 'Offer' or 'Need'
        'product': data['product'],
        'quantity': int(data['quantity']),
        'location': data['location'],
        'city': data.get('city', ''),
        'pincode': data.get('pincode', ''),
        'collaboration_type': data['collaboration_type'],
        'validity_time': datetime.fromisoformat(data['validity_time'].replace('Z', '+00:00')),
        'urgency': data.get('urgency', 'medium'),
        'description': data.get('description', ''),
        'status': 'active',
        'created_at': datetime.utcnow()
    }
    
    result = listings.insert_one(listing)
    listing['_id'] = str(result.inserted_id)
    listing['user_id'] = str(listing['user_id'])
    
    # Send notifications to matching vendors
    send_notifications(listing)
    
    return jsonify({'message': 'Listing created successfully', 'listing': listing}), 201

@app.route('/api/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = listings.find_one({'_id': ObjectId(listing_id)})
    if not listing:
        return jsonify({'message': 'Listing not found'}), 404
    
    listing['_id'] = str(listing['_id'])
    listing['user_id'] = str(listing['user_id'])
    
    # Get user details
    user = users.find_one({'_id': ObjectId(listing['user_id'])})
    if user:
        listing['vendor_name'] = user['name']
        listing['vendor_trust_score'] = user['trust_score']
    
    return jsonify({'listing': listing})

@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transaction(current_user):
    data = request.get_json()
    
    transaction = {
        'buyer_id': ObjectId(current_user['_id']),
        'seller_id': ObjectId(data['seller_id']),
        'listing_id': ObjectId(data['listing_id']),
        'type': data['type'],  # 'buy', 'group_buy', 'lend'
        'quantity': int(data['quantity']),
        'amount': float(data.get('amount', 0)),
        'status': 'pending',
        'payment_method': data.get('payment_method', 'in_app'),
        'logistics': data.get('logistics', {}),
        'supplier_logistic_charges': float(data.get('supplier_logistic_charges', 0)),
        'created_at': datetime.utcnow()
    }
    #
    result = transactions.insert_one(transaction)
    transaction['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Transaction created successfully', 'transaction': transaction}), 201

@app.route('/api/transactions/<transaction_id>/complete', methods=['PUT'])
@token_required
def complete_transaction(current_user, transaction_id):
    transaction = transactions.find_one({'_id': ObjectId(transaction_id)})
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    # Update transaction status
    transactions.update_one(
        {'_id': ObjectId(transaction_id)},
        {'$set': {'status': 'completed', 'completed_at': datetime.utcnow()}}
    )
    
    # Update user transaction counts
    users.update_one(
        {'_id': transaction['buyer_id']},
        {'$inc': {'total_transactions': 1}}
    )
    users.update_one(
        {'_id': transaction['seller_id']},
        {'$inc': {'total_transactions': 1}}
    )
    
    return jsonify({'message': 'Transaction completed successfully'})

@app.route('/api/chat', methods=['POST'])
@token_required
def send_message(current_user):
    data = request.get_json()
    
    message = {
        'sender_id': ObjectId(current_user['_id']),
        'receiver_id': ObjectId(data['receiver_id']),
        'listing_id': ObjectId(data.get('listing_id')),
        'message': data['message'],
        'created_at': datetime.utcnow()
    }
    
    result = chats.insert_one(message)
    message['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Message sent successfully', 'chat': message}), 201

@app.route('/api/chat/<user_id>', methods=['GET'])
@token_required
def get_chat_history(current_user, user_id):
    # Get chat messages between current user and specified user
    messages = []
    for msg in chats.find({
        '$or': [
            {'sender_id': ObjectId(current_user['_id']), 'receiver_id': ObjectId(user_id)},
            {'sender_id': ObjectId(user_id), 'receiver_id': ObjectId(current_user['_id'])}
        ]
    }).sort('created_at', 1):
        msg['_id'] = str(msg['_id'])
        messages.append(msg)
    
    return jsonify({'messages': messages})

@app.route('/api/feedback', methods=['POST'])
@token_required
def submit_feedback(current_user):
    data = request.get_json()
    
    feedback_data = {
        'rater_id': ObjectId(current_user['_id']),
        'rated_user_id': ObjectId(data['rated_user_id']),
        'transaction_id': ObjectId(data.get('transaction_id')),
        'rating': int(data['rating']),
        'comment': data.get('comment', ''),
        'created_at': datetime.utcnow()
    }
    
    result = feedback.insert_one(feedback_data)
    
    # Update user's trust score
    update_trust_score(data['rated_user_id'])
    
    return jsonify({'message': 'Feedback submitted successfully'}), 201

def update_trust_score(user_id):
    # Calculate average rating for user
    pipeline = [
        {'$match': {'rated_user_id': ObjectId(user_id)}},
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
    ]
    
    result = list(feedback.aggregate(pipeline))
    if result:
        avg_rating = result[0]['avg_rating']
        users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'trust_score': round(avg_rating, 1)}}
        )

def send_notifications(listing):
    # Find vendors with matching criteria
    matching_vendors = users.find({
        'location': {'$regex': listing['city'], '$options': 'i'},
        '_id': {'$ne': ObjectId(listing['user_id'])}
    })
    
    # In a real app, you would send SMS/Email here
    # For now, we'll just log the notifications
    for vendor in matching_vendors:
        print(f"Notification sent to {vendor['email']} for {listing['product']}")

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    # Get top traders
    top_traders = list(users.find().sort('total_transactions', -1).limit(5))
    for trader in top_traders:
        trader['_id'] = str(trader['_id'])
    
    # Get average fulfillment speed (mock data for now)
    avg_speed = 1.2
    
    # Get quality score
    pipeline = [
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
    ]
    result = list(feedback.aggregate(pipeline))
    quality_score = round(result[0]['avg_rating'], 1) if result else 4.8
    
    analytics_data = {
        'top_traders': top_traders,
        'avg_fulfillment_speed': avg_speed,
        'quality_score': quality_score,
        'total_listings': listings.count_documents({}),
        'total_transactions': transactions.count_documents({'status': 'completed'}),
        'active_users': users.count_documents({})
    }
    
    return jsonify(analytics_data)

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user['_id'] = str(user['_id'])
    del user['password']
    
    return jsonify({'user': user})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
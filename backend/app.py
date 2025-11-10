from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask import abort
from datetime import datetime
import os
from flask import send_from_directory
import re
import logging
import json
from functools import wraps
import requests
import google.generativeai as genai
from PIL import Image # Import Image from PIL
import io # Import io for handling image bytes

# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
# from PIL import Image  # Commented out for now

# Import security modules
from config import Config
from security import SecurityUtils
# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Configure Gemini API
gemini_vision_model = None # Initialize to None
if Config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Initialize Gemini Vision Pro model
        gemini_vision_model = genai.GenerativeModel('models/gemini-2.5-flash')
        logger.info("Gemini API configured and model initialized.")
    except Exception as e:
        logger.error(f"Error initializing Gemini API: {e}")
        logger.warning("Gemini API features will be disabled due to initialization error.")
else:
    logger.warning("GEMINI_API_KEY not found. Gemini API features will be disabled.")

# Secure CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": Config.ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
        "supports_credentials": True
    }
})

# MongoDB setup with environment variable
mongo_client = MongoClient(Config.MONGODB_URI)
db = mongo_client[Config.DATABASE_NAME]

# Collections
users_collection = db['users']
suppliers_collection = db['suppliers']
stocks_collection = db['stocks']
coupons_collection = db['coupons']
admins_collection = db['admins']
orders_collection = db['orders']

# Vendor-specific collections
vendor_users = db['vendor_users']
vendor_listings = db['vendor_listings']
vendor_transactions = db['vendor_transactions']
vendor_chats = db['vendor_chats']
vendor_feedback = db['vendor_feedback']
vendor_analytics = db['vendor_analytics']

# Payment collections
payments_collection = db['payments']

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Allowed image extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize admin collection with default admin if not exists
def initialize_admin():
    """Initialize admin collection with default admin account"""
    admin_collection = db['admins']
    
    # Create default admin accounts
    default_admins = [
        {
            'email': 'admin@overxchange.com',
            'password': generate_password_hash('admin123'),
            'name': 'System Administrator',
            'role': 'super_admin',
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'email': 'admin@gmail.com',
            'password': generate_password_hash('admin'),
            'name': 'Admin User',
            'role': 'admin',
            'created_at': datetime.utcnow(),
            'is_active': True
        }
    ]
    
    # Check and create admin accounts if they don't exist
    for admin_data in default_admins:
        existing_admin = admin_collection.find_one({'email': admin_data['email']})
        if not existing_admin:
            admin_collection.insert_one(admin_data)
            print(f"Admin account created: {admin_data['email']} / {admin_data['password'][:10]}...")
        else:
            print(f"Admin account already exists: {admin_data['email']}")

# Initialize admin on startup
initialize_admin()

# Serve frontend static files
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = SecurityUtils.verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(request.user, *args, **kwargs)
    return decorated_function

# Rate limiting decorator
def rate_limit(max_requests=100, window=3600):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            key = f"rate_limit:{client_ip}:{f.__name__}"
            
            # Simple in-memory rate limiting (use Redis in production)
            if not hasattr(app, 'rate_limit_store'):
                app.rate_limit_store = {}
            
            current_time = datetime.utcnow()
            if key in app.rate_limit_store:
                requests, timestamp = app.rate_limit_store[key]
                if (current_time - timestamp).seconds < window:
                    if requests >= max_requests:
                        SecurityUtils.log_security_event('RATE_LIMIT_EXCEEDED', details=f'IP: {client_ip}')
                        return jsonify({'error': 'Rate limit exceeded'}), 429
                    app.rate_limit_store[key] = (requests + 1, timestamp)
                else:
                    app.rate_limit_store[key] = (1, current_time)
            else:
                app.rate_limit_store[key] = (1, current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    else:
        return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/vendor-dashboard')
def vendor_dashboard():
    return send_from_directory(FRONTEND_DIR, 'vendor-dashboard.html')


@app.route('/api/login', methods=['POST'])
@rate_limit(max_requests=5, window=300)  # 5 attempts per 5 minutes
def login():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        username = SecurityUtils.sanitize_input(data.get('username', ''))
        password = data.get('password', '')
        logger.info(f"Login attempt for user: {username}")
        
        # Validate input
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        if not SecurityUtils.validate_email(username):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Try admin first
        user = db['admins'].find_one({'email': username})
        user_type = 'admin'
        
        if not user:
            # Try vendor
            user = db['vendors'].find_one({'email': username})
            user_type = 'vendor'
        
        if not user:
            # Try supplier
            user = db['suppliers'].find_one({'email': username})
            user_type = 'supplier' if user else None
        
        if not user:
            SecurityUtils.log_security_event('LOGIN_FAILED', details=f'User not found: {username}')
            logger.warning(f"Login failed: User not found for {username}")
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if not SecurityUtils.verify_password(password, user['password']):
            SecurityUtils.log_security_event('LOGIN_FAILED', user_id=str(user['_id']), details='Incorrect password')
            return jsonify({'success': False, 'message': 'Incorrect password'}), 401
        
        # Generate JWT token
        token = SecurityUtils.generate_jwt_token(str(user['_id']), user_type)
        
        SecurityUtils.log_security_event('LOGIN_SUCCESS', user_id=str(user['_id']))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_type': user_type,
            'user_id': str(user['_id']),
            'token': token
        })
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        SecurityUtils.log_security_event('LOGIN_ERROR', details=str(e))
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/signup/vendor', methods=['POST'])
@rate_limit(max_requests=3, window=3600)  # 3 signups per hour
def signup_vendor():
    try:
        data = request.json
        logger.info(f"Received vendor signup request with data: {data}")
        if not data:
            return jsonify({"success": False, "message": "Invalid request data"}), 400
        
        # Sanitize and validate input
        email = SecurityUtils.sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        first_name = SecurityUtils.sanitize_input(data.get('first_name', ''))
        last_name = SecurityUtils.sanitize_input(data.get('last_name', ''))
        name = f"{first_name} {last_name}".strip()
        phone = SecurityUtils.sanitize_input(data.get('phone', ''))
        address = SecurityUtils.sanitize_input(data.get('address', ''))
        
        # Validate required fields
        if not email or not password or not name:
            return jsonify({"success": False, "message": "Email, password, and name are required"}), 400
        
        # Validate email format
        if not SecurityUtils.validate_email(email):
            return jsonify({"success": False, "message": "Invalid email format"}), 400
        
        # Validate password strength
        password_validation = SecurityUtils.validate_password(password)
        if not password_validation['valid']:
            return jsonify({"success": False, "message": "Password validation failed", "errors": password_validation['errors']}), 400
        
        # Validate phone number if provided
        if phone and not SecurityUtils.validate_phone_number(phone):
            return jsonify({"success": False, "message": "Invalid phone number format"}), 400
        
        # Check if user already exists
        existing_user = db['vendors'].find_one({'email': email})
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 409
        
        # Hash password and create user
        hashed_password = SecurityUtils.hash_password(password)
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'phone': phone,
            'address': address,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        
        result = db['vendors'].insert_one(user_data)
        
        SecurityUtils.log_security_event('SIGNUP_SUCCESS', user_id=str(result.inserted_id), details='Vendor signup')
        
        return jsonify({"success": True, "message": "Vendor signup successful!", "id": str(result.inserted_id)})
    
    except Exception as e:
        logger.error(f"Vendor signup error: {str(e)}")
        SecurityUtils.log_security_event('SIGNUP_ERROR', details=f'Vendor signup error: {str(e)}')
        return jsonify({"success": False, "message": "Internal server error"}), 500

@app.route('/api/signup/supplier', methods=['POST'])
@rate_limit(max_requests=3, window=3600)  # 3 signups per hour
def signup_supplier():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Invalid request data"}), 400
        
        # Sanitize and validate input
        email = SecurityUtils.sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        first_name = SecurityUtils.sanitize_input(data.get('first_name', ''))
        last_name = SecurityUtils.sanitize_input(data.get('last_name', ''))
        name = f"{first_name} {last_name}".strip()
        phone = SecurityUtils.sanitize_input(data.get('phone', ''))
        address = SecurityUtils.sanitize_input(data.get('address', ''))
        
        # Validate required fields
        if not email or not password or not name:
            return jsonify({"success": False, "message": "Email, password, and name are required"}), 400
        
        # Validate email format
        if not SecurityUtils.validate_email(email):
            return jsonify({"success": False, "message": "Invalid email format"}), 400
        
        # Validate password strength
        password_validation = SecurityUtils.validate_password(password)
        if not password_validation['valid']:
            return jsonify({"success": False, "message": "Password validation failed", "errors": password_validation['errors']}), 400
        
        # Validate phone number if provided
        if phone and not SecurityUtils.validate_phone_number(phone):
            return jsonify({"success": False, "message": "Invalid phone number format"}), 400
        
        # Check if user already exists
        existing_user = db['suppliers'].find_one({'email': email})
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 409
        
        # Hash password and create user
        hashed_password = SecurityUtils.hash_password(password)
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'phone': phone,
            'address': address,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        
        result = db['suppliers'].insert_one(user_data)
        
        SecurityUtils.log_security_event('SIGNUP_SUCCESS', user_id=str(result.inserted_id), details='Supplier signup')
        
        return jsonify({"success": True, "message": "Supplier signup successful!", "id": str(result.inserted_id)})
    
    except Exception as e:
        logger.error(f"Supplier signup error: {str(e)}")
        SecurityUtils.log_security_event('SIGNUP_ERROR', details=f'Supplier signup error: {str(e)}')
        return jsonify({"success": False, "message": "Internal server error"}), 500

def get_user_collection(user_type):
    if user_type == 'vendor':
        return db['vendors']
    elif user_type == 'supplier':
        return db['suppliers']
    else:
        abort(400, 'Invalid user type')

@app.route('/api/profile/<user_type>/<user_id>', methods=['GET'])
@require_auth
@rate_limit(max_requests=100, window=3600)
def get_profile(current_user, user_type, user_id):
    try:
        # Verify user can access this profile
        if current_user['user_id'] != user_id or current_user['user_type'] != user_type:
            SecurityUtils.log_security_event('UNAUTHORIZED_ACCESS', user_id=current_user['user_id'], details=f'Attempted to access {user_type}/{user_id}')
            return jsonify({'error': 'Unauthorized access'}), 403
        
        collection = get_user_collection(user_type)
        user = collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove sensitive data
        user.pop('password', None)
        user['user_type'] = user_type
        user['user_id'] = str(user['_id'])
        user['_id'] = str(user['_id'])
        
        return jsonify(user)
    
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profile/<user_type>/<user_id>', methods=['PUT'])
@require_auth
@rate_limit(max_requests=50, window=3600)
def update_profile(current_user, user_type, user_id):
    try:
        # Verify user can update this profile
        if current_user['user_id'] != user_id or current_user['user_type'] != user_type:
            SecurityUtils.log_security_event('UNAUTHORIZED_ACCESS', user_id=current_user['user_id'], details=f'Attempted to update {user_type}/{user_id}')
            return jsonify({'error': 'Unauthorized access'}), 403
        
        collection = get_user_collection(user_type)
        data = request.json
        
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        # Sanitize input data
        sanitized_data = {}
        allowed_fields = ['name', 'phone', 'address', 'company_name', 'business_type']
        
        for field in allowed_fields:
            if field in data:
                sanitized_data[field] = SecurityUtils.sanitize_input(str(data[field]))
        
        if not sanitized_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user profile
        result = collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': sanitized_data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'User not found or no changes made'}), 404
        
        SecurityUtils.log_security_event('PROFILE_UPDATED', user_id=user_id)
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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
        if not stock.get('image_url'):
            stock['image_url'] = f"https://via.placeholder.com/150/808080/FFFFFF?text={stock.get('product_name', 'Product').replace(' ', '+')}"
    return jsonify({'success': True, 'stocks': stocks})

@app.route('/api/stocks/supplier/<supplier_id>', methods=['GET'])
def get_supplier_stocks(supplier_id):
    """Get stocks for a specific supplier"""
    stocks = list(db['stocks'].find({'supplier_id': supplier_id}))
    for stock in stocks:
        stock['_id'] = str(stock['_id'])
        stock['supplier_id'] = str(stock['supplier_id'])
        if not stock.get('image_url'):
            stock['image_url'] = f"https://via.placeholder.com/150/808080/FFFFFF?text={stock.get('product_name', 'Product').replace(' ', '+')}"
    return jsonify({'success': True, 'stocks': stocks})

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """Add a new stock item"""
    try:
        data = request.form.to_dict()
        
        # Convert numeric fields from string
        numeric_fields = ['quantity_available', 'price_per_unit', 'minimum_order_quantity', 'weight']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    data[field] = 0

        data['is_organic'] = data.get('is_organic', 'false').lower() == 'true'
        
        # Handle image upload
        if 'product_image' in request.files:
            image_file = request.files['product_image']
            if image_file and image_file.filename != '':
                if not allowed_file(image_file.filename):
                    return jsonify({'success': False, 'message': 'Invalid file type. Please upload an image (png, jpg, jpeg, gif, webp).'}), 400
                filename = SecurityUtils.sanitize_filename(image_file.filename)
                
                try:
                    token = os.environ.get('BLOB_READ_WRITE_TOKEN')
                    if not token:
                        logger.error("BLOB_READ_WRITE_TOKEN not set.")
                        return jsonify({'success': False, 'message': 'Image storage is not configured.'}), 500

                    headers = {
                        'x-api-version': '5',
                        'authorization': f'Bearer {token}',
                        'x-content-type': image_file.mimetype
                    }
                    
                    upload_url = f'https://blob.vercel-storage.com/{filename}'
                    
                    file_content = image_file.read()

                    response = requests.put(
                        upload_url,
                        data=file_content,
                        headers=headers,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    blob_data = response.json()
                    data['image_url'] = blob_data['url']

                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to upload image to Vercel Blob: {e}")
                    return jsonify({'success': False, 'message': 'Error uploading image.'}), 500
                except Exception as e:
                    logger.error(f"An unexpected error occurred during image upload: {e}")
                    return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['last_updated'] = datetime.now()
        data['stock_history'] = [{
            'action': 'stock_added',
            'quantity_change': data.get('quantity_available', 0),
            'previous_stock': 0,
            'new_stock': data.get('quantity_available', 0),
            'timestamp': datetime.now()
        }]
        result = db['stocks'].insert_one(data)
        return jsonify({'success': True, 'message': 'Stock added successfully!', 'id': str(result.inserted_id)})
    except Exception as e:
        logger.error(f"Error adding stock: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/stocks/<stock_id>', methods=['PUT'])
def update_stock(stock_id):
    """Update a stock item"""
    try:
        data = request.form.to_dict()

        # Convert numeric fields from string
        numeric_fields = ['quantity_available', 'price_per_unit', 'minimum_order_quantity', 'weight']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    # Keep existing value if conversion fails
                    pass

        data['is_organic'] = data.get('is_organic', 'false').lower() == 'true'

        # Handle image upload
        if 'product_image' in request.files:
            image_file = request.files['product_image']
            if image_file.filename != '':
                filename = SecurityUtils.sanitize_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                data['image_url'] = filename
        
        # Get current stock to calculate quantity change
        current_stock = db['stocks'].find_one({'_id': ObjectId(stock_id)})
        if not current_stock:
            return jsonify({'success': False, 'message': 'Stock not found'}), 404
        
        current_quantity = current_stock.get('quantity_available', 0)
        new_quantity = float(data.get('quantity_available', current_quantity))
        quantity_change = new_quantity - current_quantity
        current_quantity = current_stock.get('quantity_available', 0)
        new_quantity = data.get('quantity_available', current_quantity)
        quantity_change = float(new_quantity) - float(current_quantity)
        
        # Prepare update data
        update_data = data.copy()
        update_data['updated_at'] = datetime.now()
        update_data['last_updated'] = datetime.now()
        
        # Add stock history entry
        stock_history_entry = {
            'action': 'stock_updated',
            'quantity_change': quantity_change,
            'previous_stock': current_quantity,
            'new_stock': new_quantity,
            'timestamp': datetime.now()
        }
        
        # Update stock with history
        result = db['stocks'].update_one(
            {'_id': ObjectId(stock_id)}, 
            {
                '$set': update_data,
                '$push': {'stock_history': stock_history_entry}
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Stock not found'}), 404
            
        return jsonify({'success': True, 'message': 'Stock updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stocks/<stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """Delete a stock item"""
    result = db['stocks'].delete_one({'_id': ObjectId(stock_id)})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Stock not found'}), 404
    return jsonify({'success': True, 'message': 'Stock deleted successfully!'})

@app.route('/api/orders', methods=['POST'])
@require_auth
def create_order(current_user):
    """Create a new order from a vendor"""
    try:
        data = request.json
        vendor_id = current_user['user_id']

        # Basic validation
        if not data.get('items'):
            return jsonify({'success': False, 'message': 'Missing order items'}), 400
        
        # Validate and structure customer_info
        customer_info = data.get('customer_info', {})
        if not all(customer_info.get(key) for key in ['firstName', 'email', 'phone']):
            return jsonify({'success': False, 'message': 'Customer first name, email, and phone are required'}), 400
        
        # Validate and structure shipping_address
        shipping_address = data.get('shipping_address', {})
        if not all(shipping_address.get(key) for key in ['addressLine1', 'city', 'state', 'pincode']):
            return jsonify({'success': False, 'message': 'Shipping address (addressLine1, city, state, pincode) is required'}), 400

        payment_method = data.get('payment_method')
        if not payment_method:
            return jsonify({'success': False, 'message': 'Payment method is required'}), 400

        # Group items by supplier
        supplier_orders = {}
        for item in data['items']:
            supplier_id = item.get('supplierId')
            if supplier_id not in supplier_orders:
                # Fetch supplier details to get the name
                supplier_doc = suppliers_collection.find_one({'_id': ObjectId(supplier_id)})
                supplier_name = supplier_doc.get('name', 'Unknown Supplier') if supplier_doc else 'Unknown Supplier'
                
                supplier_orders[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name, # Add supplier_name here
                    'items': [],
                    'subtotal': 0,
                    'status': 'pending'
                }
            supplier_orders[supplier_id]['items'].append(item)
            supplier_orders[supplier_id]['subtotal'] += item['price'] * item['quantity']

        # Create the main order document
        order_doc = {
            'vendor_id': ObjectId(vendor_id),
            'customer_info': customer_info,
            'shipping_address': shipping_address,
            'total_amount': data['total_amount'],
            'subtotal': data['subtotal'],
            'tax': data['tax'],
            'shipping_cost': data.get('shipping_cost', 0),
            'discount': data.get('discount', 0),
            'coupon_code': data.get('coupon_code'),
            'payment_method': payment_method, # Add payment method here
            'status': 'pending', # Overall order status
            'order_date': datetime.utcnow(), # Add order_date
            'created_at': datetime.utcnow(),
            'supplier_orders': list(supplier_orders.values()) # Embed supplier-specific orders
        }

        result = orders_collection.insert_one(order_doc)
        
        # Could potentially trigger stock deduction here in a real scenario

        return jsonify({'success': True, 'message': 'Order placed successfully!', 'order_id': str(result.inserted_id)})

    except Exception as e:
        logger.error(f"Order creation error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/vendor/orders', methods=['GET'])
@require_auth
def get_vendor_orders(current_user):
    """Get all orders for the currently logged-in vendor"""
    try:
        vendor_id = current_user['user_id']
        orders = list(orders_collection.find({'vendor_id': ObjectId(vendor_id)}).sort('created_at', -1))

        for order in orders:
            order['_id'] = str(order['_id'])
            order['vendor_id'] = str(order['vendor_id'])
            # Convert ObjectId in supplier_orders items as well
            for supplier_order in order.get('supplier_orders', []):
                supplier_order['supplier_id'] = str(supplier_order['supplier_id'])
                for item in supplier_order.get('items', []):
                    item['id'] = str(item['id'])

        return jsonify({'success': True, 'orders': orders})

    except Exception as e:
        logger.error(f"Get vendor orders error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/supplier/orders', methods=['GET'])
@require_auth
def get_supplier_orders(current_user):
    """Get all orders for the currently logged-in supplier"""
    try:
        supplier_id = current_user['user_id']
        
        # Find orders where this supplier is part of the supplier_orders array
        orders = list(orders_collection.find({'supplier_orders.supplier_id': supplier_id}).sort('created_at', -1))

        for order in orders:
            order['_id'] = str(order['_id'])
            order['vendor_id'] = str(order['vendor_id'])
            # Convert ObjectId in supplier_orders items as well
            for supplier_order in order.get('supplier_orders', []):
                supplier_order['supplier_id'] = str(supplier_order['supplier_id'])
                for item in supplier_order.get('items', []):
                    item['id'] = str(item['id'])

        return jsonify({'success': True, 'orders': orders})

    except Exception as e:
        logger.error(f"Get supplier orders error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
@require_auth
def get_order_details(current_user, order_id):
    """Get details for a specific order"""
    try:
        # Add validation for order_id
        if not ObjectId.is_valid(order_id):
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        order = orders_collection.find_one({'_id': ObjectId(order_id)})

        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        # Security check: Ensure the user (vendor or supplier) is part of this order
        user_id = current_user['user_id']
        user_type = current_user['user_type']

        is_vendor = user_type == 'vendor' and str(order.get('vendor_id')) == user_id
        is_supplier = user_type == 'supplier' and any(str(so.get('supplier_id')) == user_id for so in order.get('supplier_orders', []))

        if not (is_vendor or is_supplier or user_type == 'admin'):
            return jsonify({'success': False, 'message': 'Unauthorized to view this order'}), 403

        # Convert ObjectIds to strings for JSON serialization
        order['_id'] = str(order['_id'])
        if 'vendor_id' in order:
            order['vendor_id'] = str(order['vendor_id'])
        for so in order.get('supplier_orders', []):
            if 'supplier_id' in so:
                so['supplier_id'] = str(so['supplier_id'])

        return jsonify({'success': True, 'order': order})

    except Exception as e:
        logger.error(f"Get order details error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>/accept', methods=['POST'])
@require_auth
def accept_order(current_user, order_id):
    """Accept a supplier's portion of an order"""
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        supplier_id = current_user['user_id']
        data = request.json
        acceptance_notes = data.get('acceptance_notes')
        estimated_delivery = data.get('estimated_delivery')

        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        supplier_order_found = False
        stock_update_messages = []
        for so in order.get('supplier_orders', []):
            if so.get('supplier_id') == supplier_id and so.get('status') == 'pending':
                so['status'] = 'accepted'
                so['acceptance_notes'] = acceptance_notes
                so['estimated_delivery'] = estimated_delivery
                supplier_order_found = True

                for item in so.get('items', []):
                    stock_item = stocks_collection.find_one({'_id': ObjectId(item['id'])})
                    if stock_item:
                        new_quantity = stock_item.get('quantity_available', 0) - item.get('quantity', 0)
                        if new_quantity < 0:
                            stock_update_messages.append(f"Warning: Not enough stock for {item['name']}.")
                            new_quantity = 0
                        
                        stocks_collection.update_one(
                            {'_id': ObjectId(item['id'])},
                            {'$set': {'quantity_available': new_quantity, 'updated_at': datetime.utcnow()}}
                        )
                        stock_update_messages.append(f"Stock for {item['name']} updated to {new_quantity}.")
                    else:
                        stock_update_messages.append(f"Warning: Stock item with ID {item['id']} not found.")
                break
        
        if not supplier_order_found:
            return jsonify({'success': False, 'message': 'No pending order found for this supplier.'}), 400

        orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'supplier_orders': order['supplier_orders']}})
        return jsonify({'success': True, 'message': 'Order accepted successfully!', 'stock_updated': True, 'stock_message': " ".join(stock_update_messages)})

    except Exception as e:
        logger.error(f"Accept order error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>/reject', methods=['POST'])
@require_auth
def reject_order(current_user, order_id):
    """Reject a supplier's portion of an order"""
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        supplier_id = current_user['user_id']
        data = request.json
        rejection_reason = data.get('rejection_reason', 'No reason provided')

        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        supplier_order_found = False
        for so in order.get('supplier_orders', []):
            if so.get('supplier_id') == supplier_id and so.get('status') == 'pending':
                so['status'] = 'rejected'
                so['rejection_reason'] = rejection_reason
                supplier_order_found = True
                break
        
        if not supplier_order_found:
            return jsonify({'success': False, 'message': 'No pending order found for this supplier'}), 400

        orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'supplier_orders': order['supplier_orders']}})
        return jsonify({'success': True, 'message': 'Order rejected successfully!'})

    except Exception as e:
        logger.error(f"Reject order error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@require_auth
def update_order_status(current_user, order_id):
    """Update the status of a supplier's portion of an order"""
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        data = request.json
        new_status = data.get('status')
        if not new_status:
            return jsonify({'success': False, 'message': 'New status is required'}), 400

        supplier_id = current_user['user_id']

        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        supplier_order_found = False
        for so in order.get('supplier_orders', []):
            if so.get('supplier_id') == supplier_id:
                so['status'] = new_status
                supplier_order_found = True
                break
        
        if not supplier_order_found:
            return jsonify({'success': False, 'message': 'No order found for this supplier'}), 400

        orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'supplier_orders': order['supplier_orders']}})
        return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})

    except Exception as e:
        logger.error(f"Update order status error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>/delivery', methods=['PUT'])
@require_auth
def update_delivery_info(current_user, order_id):
    """Update delivery info for a supplier's portion of an order"""
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        data = request.json
        supplier_id = current_user['user_id']
        tracking_number = data.get('tracking_number')
        estimated_delivery = data.get('estimated_delivery')
        delivery_notes = data.get('delivery_notes')

        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        supplier_order_found = False
        for so in order.get('supplier_orders', []):
            if so.get('supplier_id') == supplier_id:
                if tracking_number:
                    so['tracking_number'] = tracking_number
                if estimated_delivery:
                    so['estimated_delivery'] = estimated_delivery
                if delivery_notes:
                    so['delivery_notes'] = delivery_notes
                supplier_order_found = True
                break
        
        if not supplier_order_found:
            return jsonify({'success': False, 'message': 'No order found for this supplier'}), 400

        orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'supplier_orders': order['supplier_orders']}})
        return jsonify({'success': True, 'message': 'Delivery information updated successfully!'})

    except Exception as e:
        logger.error(f"Update delivery info error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/orders/<order_id>/bill', methods=['GET'])
@require_auth
def download_bill(current_user, order_id):
    """Generate an HTML bill for a specific order"""
    try:
        if not ObjectId.is_valid(order_id):
            logger.warning(f"Invalid order ID format: {order_id}")
            return jsonify({'success': False, 'message': 'Invalid order ID format'}), 400

        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            logger.warning(f"Order not found for ID: {order_id}")
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        logger.debug(f"Full order object for bill: {json.dumps(order, default=str, indent=2)}")

        # Fetch vendor details
        vendor_id = order.get('vendor_id')
        vendor_info = None
        if vendor_id:
            logger.debug(f"Fetching vendor info for vendor_id: {vendor_id}")
            vendor_info = db['vendors'].find_one({'_id': ObjectId(vendor_id)})
            logger.debug(f"Vendor info fetched: {json.dumps(vendor_info, default=str, indent=2)}")
        else:
            logger.warning(f"vendor_id not found in order: {order_id}")

        bill_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice for Order #{str(order['_id'])}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; margin: 20px; color: #555; }}
                .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, .15); font-size: 16px; line-height: 24px; }}
                .invoice-box table {{ width: 100%; line-height: inherit; text-align: left; border-collapse: collapse; }}
                .invoice-box table td {{ padding: 8px; vertical-align: top; }}
                .invoice-box table tr.top table td {{ padding-bottom: 20px; }}
                .invoice-box table tr.information table td {{ padding-bottom: 30px; }}
                .invoice-box table tr.heading td {{ background: #eee; border-bottom: 1px solid #ddd; font-weight: bold; padding: 10px 8px; }}
                .invoice-box table tr.details td {{ padding-bottom: 20px; }}
                .invoice-box table tr.item td {{ border-bottom: 1px solid #eee; }}
                .invoice-box table tr.item.last td {{ border-bottom: none; }}
                .invoice-box table tr.total td:nth-child(2) {{ border-top: 2px solid #eee; font-weight: bold; }}
                .invoice-box .title {{ font-size: 45px; line-height: 45px; color: #333; }}
                .invoice-box .section-title {{ font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }}
                .text-right {{ text-align: right; }}
                .text-left {{ text-align: left; }}
            </style>
        </head>
        <body>
            <div class="invoice-box">
                <table>
                    <tr class="top">
                        <td colspan="2">
                            <table>
                                <tr>
                                    <td class="title"><h2>OverXchange Inc.</h2></td>
                                    <td class="text-right">
                                        Invoice #: {str(order['_id'])}<br>
                                        Created: {order.get('created_at').strftime('%B %d, %Y') if order.get('created_at') else 'N/A'}<br>
                                        Order Status: {order.get('status', 'N/A').capitalize()}<br>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr class="information">
                        <td colspan="2">
                            <table>
                                <tr>
                                    <td>
                                        <div class="section-title">Customer Details:</div>
                                        <strong>{order.get('customer_info', {}).get('firstName', 'N/A')} {order.get('customer_info', {}).get('lastName', '')}</strong><br>
                                        {order.get('shipping_address', {}).get('addressLine1', 'N/A')}<br>
                                        {order.get('shipping_address', {}).get('city', 'N/A')}, {order.get('shipping_address', {}).get('state', 'N/A')} {order.get('shipping_address', {}).get('pincode', 'N/A')}<br>
                                        Phone: {order.get('customer_info', {}).get('phone', 'N/A')}<br>
                                        Email: {order.get('customer_info', {}).get('email', 'N/A')}
                                    </td>
                                    <td class="text-right">
                                        <div class="section-title">Vendor Details:</div>
                                        <strong>{vendor_info.get('name', 'N/A') if vendor_info else 'N/A'}</strong><br>
                                        {vendor_info.get('email', 'N/A') if vendor_info else 'N/A'}<br>
                                        {vendor_info.get('phone', 'N/A') if vendor_info else 'N/A'}<br>
                                        {vendor_info.get('address', 'N/A') if vendor_info else 'N/A'}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr class="heading">
                        <td>Item Description</td>
                        <td class="text-right">Price</td>
                    </tr>
        """

        for so in order.get('supplier_orders', []):
            logger.debug(f"Processing supplier_order: {json.dumps(so, default=str, indent=2)}")
            # Fetch full supplier details if needed, otherwise use what's in so
            supplier_full_info = db['suppliers'].find_one({'_id': ObjectId(so['supplier_id'])}) if so.get('supplier_id') else None
            logger.debug(f"Supplier full info: {json.dumps(supplier_full_info, default=str, indent=2)}")
            
            bill_html += f"""
                <tr class="heading">
                    <td colspan="2">
                        Supplier: <strong>{so.get('supplier_name', 'N/A')}</strong>
                        {f"<br>Email: {supplier_full_info.get('email', 'N/A')}" if supplier_full_info and supplier_full_info.get('email') else ''}
                        {f"<br>Phone: {supplier_full_info.get('phone', 'N/A')}" if supplier_full_info and supplier_full_info.get('phone') else ''}
                        {f"<br>Est. Delivery: {so.get('estimated_delivery', 'Not specified')}"}
                        {f"<br>Tracking: {so.get('tracking_number', 'Not available')}"}
                    </td>
                </tr>
            """
            for item in so.get('items', []):
                bill_html += f"""
                    <tr class="item">
                        <td>{item.get('name', 'N/A')} (x{item.get('quantity', 0)})</td>
                        <td class="text-right">₹{item.get('price', 0) * item.get('quantity', 0):.2f}</td>
                    </tr>
                """
        
        bill_html += f"""
                    <tr class="total">
                        <td></td>
                        <td class="text-right">Payment Method: {order.get('payment_method', 'N/A')}</td>
                    </tr>
                    <tr class="total">
                        <td></td>
                        <td class="text-right">Subtotal: ₹{order.get('subtotal', 0):.2f}</td>
                    </tr>
                    <tr class="total">
                        <td></td>
                        <td class="text-right">Tax: ₹{order.get('tax', 0):.2f}</td>
                    </tr>
                    <tr class="total">
                        <td></td>
                        <td class="text-right">Shipping: ₹{order.get('shipping_cost', 0):.2f}</td>
                    </tr>
                    <tr class="total">
                        <td></td>
                        <td class="text-right">Discount: -₹{order.get('discount', 0):.2f}</td>
                    </tr>
                    <tr class="total">
                        <td></td>
                        <td class="text-right"><strong>Total: ₹{order.get('total_amount', 0):.2f}</strong></td>
                    </tr>
                </table>
                <div style="margin-top: 30px; text-align: center; font-size: 14px; color: #777;">
                    Thank you for your business!
                </div>
            </div>
        </body>
        </html>
        """
        return jsonify({'success': True, 'bill_html': bill_html})
    except Exception as e:
        logger.error(f"Download bill error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@app.route('/api/dashboard/<supplier_id>', methods=['GET'])
def get_dashboard_data(supplier_id):
    """Get dashboard analytics for a supplier"""
    try:
        # Get all stocks for the supplier
        stocks = list(db['stocks'].find({'supplier_id': supplier_id}))
        
        # Calculate analytics
        total_products = len(stocks)
        low_stock_items = len([s for s in stocks if s.get('quantity_available', 0) > 0 and s.get('quantity_available', 0) <= 10])
        out_of_stock_items = len([s for s in stocks if s.get('quantity_available', 0) == 0])
        
        # Calculate total value (current stock value)
        total_value = 0
        for s in stocks:
            quantity = s.get('quantity_available', 0)
            price = s.get('price_per_unit', 0)
            if quantity and price:
                total_value += quantity * price
        
        # Get total orders delivered for this supplier
        total_orders_delivered = 0
        delivered_orders_value = 0
        
        # Find supplier name from supplier_id
        supplier_info = db['suppliers'].find_one({'_id': ObjectId(supplier_id)})
        if supplier_info:
            supplier_name = supplier_info.get('business_name', supplier_info.get('name', ''))
            
            # Get all orders where this supplier has delivered items
            delivered_orders = db['orders'].find({
                'supplier_orders.supplier_name': supplier_name,
                'supplier_orders.status': 'delivered'
            })
            
            for order in delivered_orders:
                for supplier_order in order.get('supplier_orders', []):
                    if supplier_order.get('supplier_name') == supplier_name and supplier_order.get('status') == 'delivered':
                        total_orders_delivered += 1
                        # Calculate delivered order value
                        for item in supplier_order.get('items', []):
                            item_quantity = item.get('quantity', 0)
                            item_price = item.get('price', 0)
                            delivered_orders_value += item_quantity * item_price
        
        # Calculate left stock value (remaining inventory value)
        left_stock_value = total_value
        
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
                'left_stock_value': left_stock_value,
                'category_distribution': category_counts
            },
            'recent_stocks': recent_stocks
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Coupon Management APIs
@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    """Get all coupons for a supplier"""
    try:
        supplier_id = request.args.get('supplier_id')
        if not supplier_id:
            return jsonify({'success': False, 'message': 'Supplier ID is required'}), 400
        
        coupons = list(db['coupons'].find({'supplier_id': supplier_id}))
        
        # Convert ObjectId to string for JSON serialization
        for coupon in coupons:
            coupon['_id'] = str(coupon['_id'])
            coupon['supplier_id'] = str(coupon['supplier_id'])
        
        return jsonify({'success': True, 'coupons': coupons})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/coupons', methods=['POST'])
def create_coupon():
    """Create a new coupon"""
    try:
        data = request.json
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['used_count'] = 0
        
        # Validate required fields
        required_fields = ['code', 'title', 'discount_type', 'discount_value', 'min_order_amount', 'valid_from', 'valid_until', 'usage_limit', 'supplier_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Check if coupon code already exists
        existing_coupon = db['coupons'].find_one({'code': data['code'], 'supplier_id': data['supplier_id']})
        if existing_coupon:
            return jsonify({'success': False, 'message': 'Coupon code already exists'}), 400
        
        result = db['coupons'].insert_one(data)
        data['_id'] = str(result.inserted_id)
        
        return jsonify({'success': True, 'message': 'Coupon created successfully!', 'coupon': data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/coupons/<coupon_id>', methods=['PUT'])
def update_coupon(coupon_id):
    """Update a coupon"""
    try:
        data = request.json
        data['updated_at'] = datetime.now()
        
        # Remove fields that shouldn't be updated
        data.pop('_id', None)
        data.pop('created_at', None)
        data.pop('used_count', None)
        
        result = db['coupons'].update_one({'_id': ObjectId(coupon_id)}, {'$set': data})
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Coupon not found'}), 404
        
        return jsonify({'success': True, 'message': 'Coupon updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/coupons/<coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    """Delete a coupon"""
    try:
        result = db['coupons'].delete_one({'_id': ObjectId(coupon_id)})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Coupon not found'}), 404
        
        return jsonify({'success': True, 'message': 'Coupon deleted successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/coupons/<coupon_id>/redeem', methods=['POST'])
def redeem_coupon(coupon_id):
    """Redeem a coupon"""
    try:
        coupon = db['coupons'].find_one({'_id': ObjectId(coupon_id)})
        
        if not coupon:
            return jsonify({'success': False, 'message': 'Coupon not found'}), 404
        
        # Check if coupon is active
        if coupon['status'] != 'active':
            return jsonify({'success': False, 'message': 'Coupon is not active'}), 400
        
        # Check if coupon has expired
        valid_until = coupon['valid_until']
        if isinstance(valid_until, str):
            valid_until = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        
        if datetime.now() > valid_until:
            return jsonify({'success': False, 'message': 'Coupon has expired'}), 400
        
        # Check usage limit
        if coupon['used_count'] >= coupon['usage_limit']:
            return jsonify({'success': False, 'message': 'Coupon usage limit reached'}), 400
        
        # Increment used count
        db['coupons'].update_one(
            {'_id': ObjectId(coupon_id)}, 
            {'$inc': {'used_count': 1}}
        )
        
        return jsonify({
            'success': True, 
            'message': 'Coupon redeemed successfully!',
            'discount_type': coupon['discount_type'],
            'discount_value': coupon['discount_value'],
            'max_discount': coupon.get('max_discount', None)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/coupons/validate/<coupon_code>', methods=['POST'])
def validate_coupon(coupon_code):
    """Validate a coupon code"""
    try:
        data = request.json
        supplier_id = data.get('supplier_id')
        order_amount = data.get('order_amount', 0)
        
        if not supplier_id:
            return jsonify({'success': False, 'message': 'Supplier ID is required'}), 400
        
        coupon = db['coupons'].find_one({
            'code': coupon_code.upper(),
            'supplier_id': supplier_id
        })
        
        if not coupon:
            return jsonify({'success': False, 'message': 'Invalid coupon code'}), 404
        
        # Check if coupon is active
        if coupon['status'] != 'active':
            return jsonify({'success': False, 'message': 'Coupon is not active'}), 400
        
        # Check if coupon has expired
        valid_until = coupon['valid_until']
        if isinstance(valid_until, str):
            valid_until = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        
        if datetime.now() > valid_until:
            return jsonify({'success': False, 'message': 'Coupon has expired'}), 400
        
        # Check minimum order amount
        if order_amount < coupon['min_order_amount']:
            return jsonify({
                'success': False, 
                'message': f'Minimum order amount of ₹{coupon["min_order_amount"]} required'
            }), 400
        
        # Check usage limit
        if coupon['used_count'] >= coupon['usage_limit']:
            return jsonify({'success': False, 'message': 'Coupon usage limit reached'}), 400
        
        # Calculate discount
        discount_amount = 0
        if coupon['discount_type'] == 'percentage':
            discount_amount = (order_amount * coupon['discount_value']) / 100
            if coupon.get('max_discount'):
                discount_amount = min(discount_amount, coupon['max_discount'])
        else:
            discount_amount = coupon['discount_value']
        
        return jsonify({
            'success': True,
            'message': 'Coupon is valid!',
            'coupon': {
                'id': str(coupon['_id']),
                'code': coupon['code'],
                'title': coupon['title'],
                'discount_type': coupon['discount_type'],
                'discount_value': coupon['discount_value'],
                'discount_amount': discount_amount,
                'max_discount': coupon.get('max_discount')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/license/upload', methods=['POST'])
def verify_license_endpoint():
    """
    API endpoint to upload a license file and verify it using Gemini.
    """
    if 'license_file' not in request.files:
        return jsonify({'success': False, 'message': 'No license_file part in the request'}), 400
    
    license_file = request.files['license_file']
    
    if license_file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if license_file:
        file_content = license_file.read()
        file_type = license_file.content_type
        
        logger.info(f"Received file for license verification: {license_file.filename} ({file_type})")
        
        verification_result = verify_license_automatically(file_content, file_type)
        
        if verification_result.get('is_valid'):
            return jsonify({
                'success': True,
                'message': 'License verified successfully!',
                'verification_details': verification_result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'License verification failed.',
                'verification_details': verification_result
            }), 400
    
    return jsonify({'success': False, 'message': 'Something went wrong during file upload.'}), 500

# Vendor-specific routes
@app.route('/api/vendor/register', methods=['POST'])
@rate_limit(max_requests=3, window=3600)
def vendor_register():
    data = request.get_json()
    
    # Check if user already exists
    if vendor_users.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 400
    
    # Hash password
    hashed_password = generate_password_hash(data['password'])
    
    # Create user
    user = {
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'company': data.get('company', ''),
        'address': data.get('address', ''), # Changed from 'location' to 'address'
        'phone': data.get('phone', ''),
        'trust_score': 5.0,
        'total_transactions': 0,
        'created_at': datetime.utcnow()
    }
    
    result = vendor_users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    del user['password']
    
    return jsonify({'message': 'User registered successfully', 'user': user}), 201

@app.route('/api/vendor/login', methods=['POST'])
@rate_limit(max_requests=5, window=300)
def vendor_login():
    data = request.get_json()
    
    user = vendor_users.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = SecurityUtils.generate_jwt_token({
        'user_id': str(user['_id']),
        'email': user['email'],
        'user_type': 'vendor'
    })
    
    
    
    user['_id'] = str(user['_id'])
    del user['password']
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user
    })

@app.route('/api/vendor/listings', methods=['GET'])
def get_vendor_listings():
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
    for listing in vendor_listings.find(filter_query).sort('created_at', -1):
        listing['_id'] = str(listing['_id'])
        listing['user_id'] = str(listing['user_id'])
        
        # Get user details
        user = vendor_users.find_one({'_id': ObjectId(listing['user_id'])})
        if user:
            listing['vendor_name'] = user['name']
            listing['vendor_trust_score'] = user['trust_score']
        
        listings_data.append(listing)
    
    return jsonify({'listings': listings_data})

@app.route('/api/vendor/listings', methods=['POST'])
@require_auth
@rate_limit(max_requests=50, window=3600)
def create_vendor_listing(current_user):
    data = request.get_json()
    
    logger.info(f"create_vendor_listing: current_user payload: {current_user}")
    
    try:
        user_obj_id = ObjectId(current_user['user_id'])
    except Exception as e:
        logger.error(f"Invalid user_id in token: {current_user.get('user_id')} - Error: {e}")
        return jsonify({'message': 'Invalid user ID in authentication token'}), 400

    listing = {
        'user_id': user_obj_id,
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
    
    result = vendor_listings.insert_one(listing)
    listing['_id'] = str(result.inserted_id)
    listing['user_id'] = str(listing['user_id'])
    
    # Send notifications to matching vendors
    send_vendor_notifications(listing)
    
    return jsonify({'message': 'Listing created successfully', 'listing': listing}), 201

@app.route('/api/vendor/listings/<listing_id>', methods=['GET'])
def get_vendor_listing(listing_id):
    listing = vendor_listings.find_one({'_id': ObjectId(listing_id)})
    if not listing:
        return jsonify({'message': 'Listing not found'}), 404
    
    listing['_id'] = str(listing['_id'])
    listing['user_id'] = str(listing['user_id'])
    
    # Get user details
    user = vendor_users.find_one({'_id': ObjectId(listing['user_id'])})
    if user:
        listing['vendor_name'] = user['name']
        listing['vendor_trust_score'] = user['trust_score']
    
    return jsonify({'listing': listing})

@app.route('/api/vendor/transactions', methods=['POST'])
@require_auth
@rate_limit(max_requests=100, window=3600)
def create_vendor_transaction(current_user):
    data = request.get_json()
    
    transaction = {
        'buyer_id': ObjectId(current_user['user_id']),
        'seller_id': ObjectId(data['seller_id']),
        'listing_id': ObjectId(data['listing_id']),
        'type': data['type'],  # 'buy', 'group_buy', 'lend'
        'quantity': int(data['quantity']),
        'amount': float(data.get('amount', 0)),
        'status': 'pending',
        'payment_method': data.get('payment_method', 'in_app'),
        'logistics': data.get('logistics', {}),
        'created_at': datetime.utcnow()
    }
    
    result = vendor_transactions.insert_one(transaction)
    transaction['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Transaction created successfully', 'transaction': transaction}), 201

@app.route('/api/vendor/transactions/<transaction_id>/complete', methods=['PUT'])
@require_auth
@rate_limit(max_requests=50, window=3600)
def complete_vendor_transaction(current_user, transaction_id):
    transaction = vendor_transactions.find_one({'_id': ObjectId(transaction_id)})
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    # Update transaction status
    vendor_transactions.update_one(
        {'_id': ObjectId(transaction_id)},
        {'$set': {'status': 'completed', 'completed_at': datetime.utcnow()}}
    )
    
    # Update user transaction counts
    vendor_users.update_one(
        {'_id': transaction['buyer_id']},
        {'$inc': {'total_transactions': 1}}
    )
    vendor_users.update_one(
        {'_id': transaction['seller_id']},
        {'$inc': {'total_transactions': 1}}
    )
    
    return jsonify({'message': 'Transaction completed successfully'})

@app.route('/api/vendor/chat', methods=['POST'])
@require_auth
@rate_limit(max_requests=200, window=3600)
def send_vendor_message(current_user):
    data = request.get_json()
    
    message = {
        'sender_id': ObjectId(current_user['user_id']),
        'receiver_id': ObjectId(data['receiver_id']),
        'listing_id': ObjectId(data.get('listing_id')),
        'message': data['message'],
        'created_at': datetime.utcnow()
    }
    
    result = vendor_chats.insert_one(message)
    message['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Message sent successfully', 'chat': message}), 201

@app.route('/api/vendor/chat/<user_id>', methods=['GET'])
@require_auth
@rate_limit(max_requests=100, window=3600)
def get_vendor_chat_history(current_user, user_id):
    # Get chat messages between current user and specified user
    messages = []
    for msg in vendor_chats.find({
        '$or': [
            {'sender_id': ObjectId(current_user['user_id']), 'receiver_id': ObjectId(user_id)},
            {'sender_id': ObjectId(user_id), 'receiver_id': ObjectId(current_user['user_id'])}
        ]
    }).sort('created_at', 1):
        msg['_id'] = str(msg['_id'])
        messages.append(msg)
    
    return jsonify({'messages': messages})

@app.route('/api/vendor/feedback', methods=['POST'])
@require_auth
@rate_limit(max_requests=50, window=3600)
def submit_vendor_feedback(current_user):
    data = request.get_json()
    
    feedback_data = {
        'rater_id': ObjectId(current_user['user_id']),
        'rated_user_id': ObjectId(data['rated_user_id']),
        'transaction_id': ObjectId(data.get('transaction_id')),
        'rating': int(data['rating']),
        'comment': data.get('comment', ''),
        'created_at': datetime.utcnow()
    }
    
    result = vendor_feedback.insert_one(feedback_data)
    
    # Update user's trust score
    update_vendor_trust_score(data['rated_user_id'])
    
    return jsonify({'message': 'Feedback submitted successfully'}), 201

@app.route('/api/vendor/analytics', methods=['GET'])
def get_vendor_analytics():
    # Get top traders
    top_traders = list(vendor_users.find().sort('total_transactions', -1).limit(5))
    for trader in top_traders:
        trader['_id'] = str(trader['_id'])
    
    # Get average fulfillment speed (mock data for now)
    avg_speed = 1.2
    
    # Get quality score
    pipeline = [
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
    ]
    result = list(vendor_feedback.aggregate(pipeline))
    quality_score = round(result[0]['avg_rating'], 1) if result else 4.8
    
    analytics_data = {
        'top_traders': top_traders,
        'avg_fulfillment_speed': avg_speed,
        'quality_score': quality_score,
        'total_listings': vendor_listings.count_documents({}),
        'total_transactions': vendor_transactions.count_documents({'status': 'completed'}),
        'active_users': vendor_users.count_documents({})
    }
    
    return jsonify(analytics_data)

@app.route('/api/vendor/users/<user_id>', methods=['GET'])
def get_vendor_user(user_id):
    user = vendor_users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user['_id'] = str(user['_id'])
    del user['password']
    
    return jsonify({'user': user})

@app.route('/api/vendor/check_user_exists', methods=['POST'])
def check_vendor_user_exists():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    user = vendor_users.find_one({'email': email})
    if user:
        return jsonify({'exists': True, 'message': 'User exists'}), 200
    else:
        return jsonify({'exists': False, 'message': 'User does not exist'}), 200

@app.route('/api/vendor/me', methods=['GET'])
@require_auth
def get_current_vendor_user(current_user):
    # current_user is populated by the @require_auth decorator
    # It contains user_id and user_type
    user_id = current_user['user_id']
    user = vendor_users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user['_id'] = str(user['_id'])
    del user['password']
    
    return jsonify({'user': user})

def update_vendor_trust_score(user_id):
    # Calculate average rating for user
    pipeline = [
        {'$match': {'rated_user_id': ObjectId(user_id)}},
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
    ]
    
    result = list(vendor_feedback.aggregate(pipeline))
    if result:
        avg_rating = result[0]['avg_rating']
        vendor_users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'trust_score': round(avg_rating, 1)}}
        )

def send_vendor_notifications(listing):
    # Find vendors with matching criteria
    matching_vendors = vendor_users.find({
        'location': {'$regex': listing['city'], '$options': 'i'},
        '_id': {'$ne': ObjectId(listing['user_id'])}
    })
    
    # In a real app, you would send SMS/Email here
    # For now, we'll just log the notifications
    for vendor in matching_vendors:
        print(f"Notification sent to {vendor['email']} for {listing['product']}")

# License Verification System
def verify_license_automatically(file_content, file_type):
    """
    Automatically verify food license using Gemini Vision Pro for OCR and analysis.
    """
    if not Config.GEMINI_API_KEY:
        logger.error("Gemini API key not configured. License verification cannot proceed.")
        return {
            'is_valid': False,
            'confidence': 0,
            'error': 'Gemini API key not configured',
            'verification_date': datetime.now().isoformat()
        }

    try:
        text_content = ""
        image_parts = []

        if file_type.startswith('image/'):
            image = Image.open(io.BytesIO(file_content))
            image_parts.append({
                'mime_type': file_type,
                'data': io.BytesIO(file_content).getvalue()
            })
            logger.info(f"Processing image file of type: {file_type}")
        elif file_type == 'application/pdf':
            # Placeholder for PDF handling:
            # For a full implementation, you would convert each PDF page to an image
            # using a library like PyMuPDF or pdf2image, and then process each image.
            # Example (requires PyMuPDF: pip install PyMuPDF):
            # import fitz # PyMuPDF
            # doc = fitz.open(stream=file_content, filetype="pdf")
            # for page_num in range(len(doc)):
            #     page = doc.load_page(page_num)
            #     pix = page.get_pixmap()
            #     img_bytes = pix.tobytes("png")
            #     image_parts.append({
            #         'mime_type': 'image/png',
            #         'data': img_bytes
            #     })
            logger.warning("PDF processing is a placeholder. Only image files are fully supported for Gemini Vision Pro.")
            return {
                'is_valid': False,
                'confidence': 0,
                'error': 'PDF processing not fully implemented yet. Please upload an image.',
                'verification_date': datetime.now().isoformat()
            }
        else:
            return {
                'is_valid': False,
                'confidence': 0,
                'error': 'Unsupported file type for license verification.',
                'verification_date': datetime.now().isoformat()
            }

        prompt_parts = [
            "Analyze this document for food license verification. Extract the following information:\n",
            "- Is this a valid food license document? (Yes/No)\n",
            "- What is the License Number? (e.g., FSSAI 14-digit number or other)\n",
            "- What is the Name of the Food Business Operator/Establishment?\n",
            "- What is the Address of the Food Business?\n",
            "- What is the Date of Issue?\n",
            "- What is the Validity/Expiry Date?\n",
            "- What is the Issuing Authority? (e.g., FSSAI, State Food Safety Department)\n",
            "If any information is missing or unclear, state 'N/A'. Provide the response in a structured JSON format."
        ]

        # Add image parts to the prompt
        for img_part in image_parts:
            prompt_parts.append(img_part)
        
        logger.info("Sending request to Gemini Vision Pro for license analysis.")
        response = gemini_vision_model.generate_content(prompt_parts)
        
        gemini_output = response.text
        logger.debug(f"Gemini raw output: {gemini_output}")

        # Attempt to parse Gemini's JSON output
        try:
            # Gemini might wrap JSON in markdown, so try to extract it
            if '```json' in gemini_output:
                json_str = gemini_output.split('```json')[1].split('```')[0].strip()
            else:
                json_str = gemini_output.strip()
            
            analysis_result = json.loads(json_str)
            logger.info("Successfully parsed Gemini's JSON output.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini's JSON output: {e}. Raw output: {gemini_output}")
            # Fallback to simpler text analysis if JSON parsing fails
            analysis_result = {
                "Is this a valid food license document?": "No",
                "License Number": "N/A",
                "Name of the Food Business Operator/Establishment": "N/A",
                "Address of the Food Business": "N/A",
                "Date of Issue": "N/A",
                "Validity/Expiry Date": "N/A",
                "Issuing Authority": "N/A",
                "raw_gemini_output": gemini_output # Keep raw output for debugging
            }
            if "valid food license" in gemini_output.lower() and "yes" in gemini_output.lower():
                analysis_result["Is this a valid food license document?"] = "Yes"

        is_valid = analysis_result.get("Is this a valid food license document?", "No").lower() == "yes"
        license_number = analysis_result.get("License Number", "N/A")
        business_name = analysis_result.get("Name of the Food Business Operator/Establishment", "N/A")
        address = analysis_result.get("Address of the Food Business", "N/A")
        date_of_issue = analysis_result.get("Date of Issue", "N/A")
        validity_date = analysis_result.get("Validity/Expiry Date", "N/A")
        issuing_authority = analysis_result.get("Issuing Authority", "N/A")

        confidence = 100 if is_valid else 0 # Simple confidence for now

        verification_details = {
            'is_valid': is_valid,
            'confidence': confidence,
            'license_number': license_number,
            'business_name': business_name,
            'address': address,
            'date_of_issue': date_of_issue,
            'validity_date': validity_date,
            'issuing_authority': issuing_authority,
            'verification_date': datetime.now().isoformat(),
            'raw_gemini_output': gemini_output # For debugging/auditing
        }
        
        logger.info(f"License verification result: {verification_details}")
        return verification_details

    except Exception as e:
        logger.error(f"Error during Gemini-based license verification: {str(e)}")
        return {
            'is_valid': False,
            'confidence': 0,
            'error': f'Internal server error during AI verification: {str(e)}',
            'verification_date': datetime.now().isoformat()
        }

def verify_license_number(license_number):
    """
    Verify FSSAI license number against real FSSAI website
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import time
        import re
        
        # Multiple FSSAI verification URLs to try
        fssai_urls = [
            "https://foscos.fssai.gov.in/CFA/licenseDetails.html",
            "https://fssai.gov.in/license-search",
            "https://foscos.fssai.gov.in/CFA/searchLicense.html",
            "https://foodlicensing.fssai.gov.in/",
            "https://foscos.fssai.gov.in/CFA/licenseSearch.html",
            "https://fssai.gov.in/license-verification",
            "https://foscos.fssai.gov.in/CFA/verifyLicense.html"
        ]
        
        # Prepare request data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        
        for fssai_url in fssai_urls:
            try:
                print(f"Trying FSSAI URL: {fssai_url}")
                
                # Get the search page
                response = session.get(fssai_url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"Failed to access {fssai_url}, status: {response.status_code}")
                    continue
                
                # Parse the page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try different search approaches
                search_attempts = [
                    # Method 1: Direct POST with license number
                    {
                        'url': fssai_url,
                        'data': {'licenseNo': license_number},
                        'method': 'POST'
                    },
                    # Method 2: Search with different parameter names
                    {
                        'url': fssai_url,
                        'data': {'license_number': license_number, 'searchType': 'license'},
                        'method': 'POST'
                    },
                    # Method 3: GET request with license number
                    {
                        'url': f"{fssai_url}?licenseNo={license_number}",
                        'data': {},
                        'method': 'GET'
                    },
                    # Method 4: FSSAI specific parameters
                    {
                        'url': fssai_url,
                        'data': {'fssai_license_no': license_number, 'action': 'search'},
                        'method': 'POST'
                    },
                    # Method 5: State specific parameters
                    {
                        'url': fssai_url,
                        'data': {'license_id': license_number, 'state': 'all'},
                        'method': 'POST'
                    },
                    # Method 6: Alternative parameter names
                    {
                        'url': fssai_url,
                        'data': {'lic_no': license_number, 'search': 'true'},
                        'method': 'POST'
                    }
                ]
                
                for attempt in search_attempts:
                    try:
                        if attempt['method'] == 'POST':
                            search_response = session.post(attempt['url'], data=attempt['data'], headers=headers, timeout=20)
                        else:
                            search_response = session.get(attempt['url'], headers=headers, timeout=20)
                        
                        if search_response.status_code == 200:
                            # Check if license number appears in response
                            if license_number in search_response.text:
                                print(f"License {license_number} found on FSSAI website!")
                                
                                # Try to extract license details
                                search_soup = BeautifulSoup(search_response.content, 'html.parser')
                                
                                # Look for business name, address, etc.
                                business_name = extract_business_name(search_soup)
                                address = extract_address(search_soup)
                                validity = extract_validity(search_soup)
                                
                                return {
                                    'is_valid': True,
                                    'license_info': {
                                        'business_name': business_name or 'Verified from FSSAI Website',
                                        'address': address or 'Address from FSSAI database',
                                        'business_type': 'Food Business',
                                        'valid_from': 'Date from FSSAI database',
                                        'valid_until': validity or 'Date from FSSAI database',
                                        'status': 'active',
                                        'source': 'FSSAI Official Website'
                                    },
                                    'message': 'License verified from FSSAI official website'
                                }
                    
                    except Exception as e:
                        print(f"Search attempt failed: {e}")
                        continue
                
            except Exception as e:
                print(f"Error with URL {fssai_url}: {e}")
                continue
        
        # If all attempts fail, try alternative government websites
        print("FSSAI website verification failed, trying alternative government websites...")
        alternative_result = verify_license_alternative(license_number)
        
        if alternative_result['is_valid']:
            return alternative_result
        
        # If all verification methods fail, try working government data APIs
        print("Trying working government data APIs...")
        
        # Try data.gov.in API with proper error handling
        try:
            data_gov_response = session.get(
                'https://data.gov.in/api/fssai-licenses',
                params={
                    'api-key': '579b464db66ec23bdd000001',
                    'format': 'json',
                    'filters[license_number]': license_number
                },
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                timeout=30
            )
            
            if data_gov_response.status_code == 200:
                try:
                    data = data_gov_response.json()
                    if data.get('records') and len(data['records']) > 0:
                        record = data['records'][0]
                        return {
                            'is_valid': True,
                            'license_info': {
                                'business_name': record.get('business_name', 'Verified Business'),
                                'address': record.get('address', 'Address from Government Database'),
                                'business_type': record.get('business_type', 'Food Business'),
                                'valid_from': record.get('valid_from', 'Date from Database'),
                                'valid_until': record.get('valid_until', 'Date from Database'),
                                'status': record.get('status', 'active'),
                                'source': 'Government of India Data Portal'
                            },
                            'message': 'License verified from Government of India Data Portal'
                        }
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Data.gov.in API failed: {e}")
        
        # Final fallback - proper error message
        return {
            'is_valid': False,
            'message': 'License verification failed. Government APIs are currently not accessible. Please try again later or contact FSSAI directly.',
            'license_info': None
        }
        
    except Exception as e:
        print(f"Error in real verification: {e}")
        # Return proper error response
        return {
            'is_valid': False,
            'message': f'Error verifying license: {str(e)}',
            'license_info': None
        }

def extract_business_name(soup):
    """Extract business name from FSSAI page"""
    try:
        # Common selectors for business name
        selectors = [
            '.business-name', '.company-name', '.firm-name',
            'td:contains("Business Name")', 'td:contains("Company Name")',
            '[data-field="business_name"]', '[data-field="company_name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback: look for text containing business-related keywords
        text = soup.get_text()
        business_patterns = [
            r'Business Name[:\s]*([^\n\r]+)',
            r'Company Name[:\s]*([^\n\r]+)',
            r'Firm Name[:\s]*([^\n\r]+)'
        ]
        
        for pattern in business_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    except:
        return None

def extract_address(soup):
    """Extract address from FSSAI page"""
    try:
        # Common selectors for address
        selectors = [
            '.address', '.business-address', '.company-address',
            'td:contains("Address")', 'td:contains("Location")',
            '[data-field="address"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback: look for address patterns
        text = soup.get_text()
        address_patterns = [
            r'Address[:\s]*([^\n\r]+)',
            r'Location[:\s]*([^\n\r]+)',
            r'Registered Address[:\s]*([^\n\r]+)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    except:
        return None

def extract_validity(soup):
    """Extract validity date from FSSAI page"""
    try:
        # Common selectors for validity
        selectors = [
            '.validity', '.valid-until', '.expiry-date',
            'td:contains("Valid Until")', 'td:contains("Expiry")',
            '[data-field="validity"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback: look for date patterns
        text = soup.get_text()
        date_patterns = [
            r'Valid Until[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Expiry Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Valid Till[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    except:
        return None

def verify_license_alternative(license_number):
    """Alternative verification methods - try other government websites"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Working government data portals and APIs
        alternative_urls = [
            # Central Government Data Portals
            "https://data.gov.in/",
            "https://api.data.gov.in/",
            "https://www.fssai.gov.in/",
            
            # State Data Portals
            "https://data.maharashtra.gov.in/",
            "https://data.karnataka.gov.in/",
            "https://data.tn.gov.in/",
            "https://data.gujarat.gov.in/",
            "https://data.delhi.gov.in/",
            "https://data.wb.gov.in/",
            "https://data.up.gov.in/",
            "https://data.bihar.gov.in/",
            "https://data.rajasthan.gov.in/",
            "https://data.mp.gov.in/",
            "https://data.ap.gov.in/",
            "https://data.telangana.gov.in/",
            "https://data.kerala.gov.in/",
            "https://data.odisha.gov.in/",
            "https://data.assam.gov.in/",
            "https://data.punjab.gov.in/",
            "https://data.haryana.gov.in/",
            "https://data.himachal.gov.in/",
            "https://data.uk.gov.in/",
            "https://data.jharkhand.gov.in/",
            "https://data.cg.gov.in/",
            "https://data.goa.gov.in/",
            
            # Additional Government APIs
            "https://api.india.gov.in/",
            "https://www.nic.in/",
            "https://www.india.gov.in/"
        ]
        
        # Also try state-specific verification
        state_verification_result = verify_license_by_state(license_number)
        if state_verification_result['is_valid']:
            return state_verification_result
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        
        for url in alternative_urls:
            try:
                print(f"Trying alternative URL: {url}")
                
                # Try to access the website
                response = session.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    # Try to search for the license
                    search_data = {
                        'licenseNo': license_number,
                        'searchType': 'license',
                        'license_number': license_number
                    }
                    
                    search_response = session.post(url, data=search_data, headers=headers, timeout=20)
                    
                    if search_response.status_code == 200 and license_number in search_response.text:
                        print(f"License {license_number} found on alternative website!")
                        
                        # Parse and extract details
                        soup = BeautifulSoup(search_response.content, 'html.parser')
                        
                        return {
                            'is_valid': True,
                            'license_info': {
                                'business_name': 'Verified from Government Website',
                                'address': 'Address from Government Database',
                                'business_type': 'Food Business',
                                'valid_from': 'Date from Government Database',
                                'valid_until': 'Date from Government Database',
                                'status': 'active',
                                'source': 'Government Alternative Website'
                            },
                            'message': 'License verified from government website'
                        }
                        
            except Exception as e:
                print(f"Alternative URL {url} failed: {e}")
                continue
        
        # If all alternative methods fail, return error
        return {
            'is_valid': False,
            'message': 'License verification failed. Unable to access government databases.'
        }
        
    except Exception as e:
        print(f"Alternative verification failed: {e}")
        return {
            'is_valid': False,
            'message': 'License verification failed. Please try again later.'
        }

def verify_license_by_state(license_number):
    """
    Verify license by trying state-specific government portals
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Working state government data portals
        state_portals = {
            'maharashtra': {
                'url': 'https://data.maharashtra.gov.in/api/food-safety-licenses',
                'method': 'GET',
                'headers': {},
                'params': {'license_number': license_number, 'state': 'maharashtra'}
            },
            'karnataka': {
                'url': 'https://data.karnataka.gov.in/api/license-verification',
                'method': 'GET',
                'headers': {},
                'params': {'fssai_license': license_number, 'state': 'karnataka'}
            },
            'tamilnadu': {
                'url': 'https://data.tn.gov.in/api/food-license/verify',
                'method': 'GET',
                'headers': {},
                'params': {'license_no': license_number, 'state': 'tamilnadu'}
            },
            'gujarat': {
                'url': 'https://data.gujarat.gov.in/api/food-safety/check',
                'method': 'GET',
                'headers': {},
                'params': {'license_id': license_number, 'state': 'gujarat'}
            },
            'delhi': {
                'url': 'https://data.delhi.gov.in/api/license-verification',
                'method': 'GET',
                'headers': {},
                'params': {'license_no': license_number, 'state': 'delhi'}
            },
            'west_bengal': {
                'url': 'https://data.wb.gov.in/api/food-license/verify',
                'method': 'GET',
                'headers': {},
                'params': {'license_number': license_number, 'state': 'west_bengal'}
            }
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        
        for state, config in state_portals.items():
            try:
                print(f"Trying {state} state portal...")
                
                if config['method'] == 'GET':
                    response = session.get(config['url'], params=config['params'], headers=headers, timeout=20)
                else:
                    response = session.post(config['url'], data=config['params'], headers=headers, timeout=20)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('is_valid') or (data.get('records') and len(data['records']) > 0):
                            return {
                                'is_valid': True,
                                'message': f'License verified from {state.title()} government portal',
                                'license_info': data.get('license_info') or data['records'][0]
                            }
                    except json.JSONDecodeError:
                        if license_number in response.text:
                             return {
                                'is_valid': True,
                                'message': f'License verified from {state.title()} government portal',
                                'license_info': {'source': f'{state.title()} Portal'}
                            }

            except Exception as e:
                print(f"State portal for {state} failed: {e}")
                continue
        
        return {'is_valid': False, 'message': 'State-level verification failed.'}
        
    except Exception as e:
        print(f"State verification failed: {e}")
        return {'is_valid': False, 'message': 'State-level verification failed.'}


# Google Sign-In Handlers
# @app.route('/api/config/google-client-id', methods=['GET'])
# def get_google_client_id():
#     return jsonify({'client_id': app.config['GOOGLE_CLIENT_ID']})
#
#
#
# @app.route('/api/auth/google', methods=['POST'])
# @rate_limit(max_requests=10, window=300)
# def google_auth():
#     try:
#         data = request.json
#         token = data.get('token')
#         if not token:
#             return jsonify({'success': False, 'message': 'No token provided'}), 400
#
#         try:
#             idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), app.config['GOOGLE_CLIENT_ID'])
#             email = idinfo['email']
#             name = idinfo.get('name', '')
#
#         except ValueError:
#             # Invalid token
#             return jsonify({'success': False, 'message': 'Invalid Google token'}), 401
#
#         # Check if user exists as a vendor or supplier
#         user = db.vendors.find_one({'email': email})
#         user_type = 'vendor'
#         if not user:
#             user = db.suppliers.find_one({'email': email})
#             user_type = 'supplier'
#
#         if user:
#             # User exists, log them in
#             # Note: This flow bypasses password check for Google-authenticated users
#             jwt_token = SecurityUtils.generate_jwt_token(str(user['_id']), user_type)
#             SecurityUtils.log_security_event('GOOGLE_LOGIN_SUCCESS', user_id=str(user['_id']))
#             return jsonify({
#                 'success': True,
#                 'message': 'Login successful',
#                 'user_type': user_type,
#                 'user_id': str(user['_id']),
#                 'name': user.get('name'),
#                 'token': jwt_token
#             })
#         else:
#             # New user, needs to select a role
#             SecurityUtils.log_security_event('GOOGLE_SIGNUP_INITIATED', details=f'Email: {email}')
#             return jsonify({
#                 'success': True, # Important: Use success=True to indicate a valid Google login, but action is needed
#                 'action': 'select_role',
#                 'message': 'New user. Please select a role to complete registration.',
#                 'email': email,
#                 'name': name,
#                 'google_token': token # Pass the token back to be used in the next step
#             })
#
#     except Exception as e:
#         logger.error(f"Google auth error: {str(e)}")
#         SecurityUtils.log_security_event('GOOGLE_AUTH_ERROR', details=str(e))
#         return jsonify({'success': False, 'message': 'Internal server error'}), 500
#
# @app.route('/api/auth/google/complete', methods=['POST'])
# @rate_limit(max_requests=5, window=300)
# def google_auth_complete():
#     try:
#         data = request.json
#         token = data.get('token')
#         role = data.get('role')
#
#         if not token or not role:
#             return jsonify({'success': False, 'message': 'Token and role are required'}), 400
#
#         if role not in ['vendor', 'supplier']:
#             return jsonify({'success': False, 'message': 'Invalid role specified'}), 400
#
#         try:
#             # Verify the token again for security
#             idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), app.config['GOOGLE_CLIENT_ID'])
#             email = idinfo['email']
#             name = idinfo.get('name', '')
#         except ValueError:
#             return jsonify({'success': False, 'message': 'Invalid Google token'}), 401
#
#         # Double-check that user doesn't exist to prevent race conditions
#         if db.vendors.find_one({'email': email}) or db.suppliers.find_one({'email': email}):
#              return jsonify({'success': False, 'message': 'User already exists.'}), 409
#
#         # Create new user in the correct collection
#         collection = db.vendors if role == 'vendor' else db.suppliers
#         user_data = {
#             'email': email,
#             'name': name,
#             'created_at': datetime.utcnow(),
#             'status': 'active',
#             'auth_method': 'google' # To indicate the user was created via Google
#         }
#         result = collection.insert_one(user_data)
#         user_id = result.inserted_id
#
#         # Log them in by generating a JWT
#         jwt_token = SecurityUtils.generate_jwt_token(str(user_id), role)
#         SecurityUtils.log_security_event('GOOGLE_SIGNUP_SUCCESS', user_id=str(user_id), details=f'Role: {role}')
#
#         return jsonify({
#             'success': True,
#             'message': 'Registration complete. Login successful.',
#             'user_type': role,
#             'user_id': str(user_id),
#             'name': name,
#             'token': jwt_token
#         })
#
#     except Exception as e:
#         logger.error(f"Google auth completion error: {str(e)}")
#         SecurityUtils.log_security_event('GOOGLE_AUTH_COMPLETE_ERROR', details=str(e))
#         return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ==================== Payment Settings & Payment Workflow APIs ====================

@app.route('/api/supplier/payment-settings/<supplier_id>', methods=['GET'])
@require_auth
def get_payment_settings(current_user, supplier_id):
    """Get payment settings for a supplier"""
    try:
        # Verify supplier owns this account or is admin
        if current_user['user_id'] != supplier_id and current_user.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        supplier = suppliers_collection.find_one({'_id': ObjectId(supplier_id)})
        if not supplier:
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404

        payment_settings = supplier.get('payment_settings', {})
        return jsonify({
            'success': True,
            'payment_settings': payment_settings
        })
    except Exception as e:
        logger.error(f"Error getting payment settings: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/supplier/payment-settings/<supplier_id>', methods=['PUT'])
@require_auth
def update_payment_settings(current_user, supplier_id):
    """Update payment settings for a supplier"""
    try:
        # Verify supplier owns this account
        if current_user['user_id'] != supplier_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        data = request.json
        payment_settings = {
            'preferred_method': data.get('preferred_method'),
            'bank_details': data.get('bank_details'),
            'upi_id': data.get('upi_id'),
            'qr_code_url': data.get('qr_code_url'),
            'updated_at': datetime.utcnow()
        }

        suppliers_collection.update_one(
            {'_id': ObjectId(supplier_id)},
            {'$set': {'payment_settings': payment_settings}}
        )

        return jsonify({
            'success': True,
            'message': 'Payment settings updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating payment settings: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/supplier/upload-qr-code', methods=['POST'])
@require_auth
def upload_qr_code(current_user):
    """Upload QR code image for supplier"""
    try:
        if 'qr_code' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['qr_code']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'qr_codes')
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        supplier_id = request.form.get('supplier_id') or current_user['user_id']
        filename = f"qr_{supplier_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(upload_dir, filename)

        file.save(filepath)

        # Generate URL (adjust based on your deployment)
        qr_code_url = f"/uploads/qr_codes/{filename}"

        return jsonify({
            'success': True,
            'qr_code_url': qr_code_url,
            'message': 'QR code uploaded successfully'
        })
    except Exception as e:
        logger.error(f"Error uploading QR code: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/supplier/payment-details/<supplier_id>', methods=['GET'])
@require_auth
def get_supplier_payment_details(current_user, supplier_id):
    """Get supplier payment details for vendor payment form"""
    try:
        supplier = suppliers_collection.find_one({'_id': ObjectId(supplier_id)})
        if not supplier:
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404

        payment_settings = supplier.get('payment_settings', {})
        preferred_method = payment_settings.get('preferred_method')

        # Calculate pending amount (sum of earnings from completed orders)
        pending_amount = 0
        completed_orders = orders_collection.find({
            'supplier_orders.supplier_id': supplier_id,
            'supplier_orders.status': {'$in': ['completed', 'delivered']}
        })

        for order in completed_orders:
            for supplier_order in order.get('supplier_orders', []):
                if str(supplier_order.get('supplier_id')) == supplier_id:
                    subtotal = supplier_order.get('subtotal', 0)
                    # Calculate earnings (95% after 5% commission)
                    earnings = subtotal * 0.95
                    pending_amount += earnings

        # Subtract already paid amounts
        paid_payments = payments_collection.find({
            'supplier_id': ObjectId(supplier_id),
            'status': {'$in': ['done', 'verification']}
        })
        for payment in paid_payments:
            pending_amount -= payment.get('amount', 0)

        payment_details = {
            'preferred_method': preferred_method,
            'bank_details': payment_settings.get('bank_details'),
            'upi_id': payment_settings.get('upi_id'),
            'qr_code_url': payment_settings.get('qr_code_url'),
            'pending_amount': max(0, pending_amount)  # Ensure non-negative
        }

        return jsonify({
            'success': True,
            'payment_details': payment_details
        })
    except Exception as e:
        logger.error(f"Error getting payment details: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/vendor/payments', methods=['POST'])
@require_auth
def create_vendor_payment(current_user):
    """Create a vendor payment to supplier"""
    try:
        data = request.json
        vendor_id = current_user['user_id']
        supplier_id = data.get('supplier_id')
        amount = float(data.get('amount', 0))
        payment_method = data.get('payment_method')
        transaction_id = data.get('transaction_id')

        if not supplier_id or not amount or not payment_method:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        if not transaction_id:
            return jsonify({'success': False, 'message': 'Transaction ID is required'}), 400

        # Verify supplier exists
        supplier = suppliers_collection.find_one({'_id': ObjectId(supplier_id)})
        if not supplier:
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404

        # Get supplier's preferred payment method
        payment_settings = supplier.get('payment_settings', {})
        preferred_method = payment_settings.get('preferred_method', 'auto')
        if payment_method == 'auto':
            payment_method = preferred_method

        # Create payment record
        payment_doc = {
            'vendor_id': ObjectId(vendor_id),
            'supplier_id': ObjectId(supplier_id),
            'amount': amount,
            'payment_method': payment_method,
            'transaction_id': transaction_id,
            'status': 'verification',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = payments_collection.insert_one(payment_doc)

        return jsonify({
            'success': True,
            'message': 'Payment submitted for verification',
            'payment_id': str(result.inserted_id)
        })
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/payments', methods=['GET'])
@require_auth
def get_payments(current_user):
    """Get payments list for supplier or admin"""
    try:
        user_id = current_user['user_id']
        user_type = current_user.get('user_type', 'supplier')

        query = {}
        if user_type == 'supplier':
            query['supplier_id'] = ObjectId(user_id)
        elif user_type == 'vendor':
            query['vendor_id'] = ObjectId(user_id)
        # Admin can see all payments

        payments = list(payments_collection.find(query).sort('created_at', -1))

        # Convert ObjectId to string
        for payment in payments:
            payment['_id'] = str(payment['_id'])
            payment['vendor_id'] = str(payment['vendor_id'])
            payment['supplier_id'] = str(payment['supplier_id'])

        return jsonify({
            'success': True,
            'payments': payments
        })
    except Exception as e:
        logger.error(f"Error getting payments: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/payments/<payment_id>/status', methods=['PUT'])
@require_auth
def update_payment_status(current_user, payment_id):
    """Update payment status (Done/Undone)"""
    try:
        data = request.json
        new_status = data.get('status')  # 'done' or 'undone'

        if new_status not in ['done', 'undone']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400

        payment = payments_collection.find_one({'_id': ObjectId(payment_id)})
        if not payment:
            return jsonify({'success': False, 'message': 'Payment not found'}), 404

        user_id = current_user['user_id']
        user_type = current_user.get('user_type', 'supplier')

        # Verify user has permission (supplier or admin)
        if user_type != 'admin' and str(payment['supplier_id']) != user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        # Update payment status
        payments_collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': {
                'status': new_status,
                'updated_at': datetime.utcnow(),
                'verified_by': user_id,
                'verified_at': datetime.utcnow()
            }}
        )

        message = 'Payment verified successfully.' if new_status == 'done' else 'Payment marked as undone.'
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Use environment variables for host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    # Turn off debug mode in production
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Start the Flask app
    app.run(host=host, port=port, debug=debug)
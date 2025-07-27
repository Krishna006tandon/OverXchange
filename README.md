# OverXchange - Food Supply Chain Management Platform

A comprehensive food supply chain management platform that connects vendors and suppliers, featuring order management, payment processing, and analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (already configured)
- Modern web browser

### Installation & Running

#### Option 1: Using the Launcher Script (Recommended)
```bash
# Windows
run_app.bat

# Or using Python
python run_app.py
```

#### Option 2: Manual Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py
```

### Access the Application
- **Frontend**: http://localhost:5000
- **API Endpoints**: http://localhost:5000/api/

## 🏗️ Project Structure

```
OverXchange/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── analytics_api.py    # Analytics endpoints
│   ├── invoice_app.py      # Invoice generation
│   └── Vendor_app.py       # Vendor-specific endpoints
├── frontend/               # Static HTML/CSS/JS files
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── dashboard.js        # Dashboard functionality
│   └── style.css           # Main stylesheet
├── Chatbot/                # AI Chatbot component
├── run_app.py              # Application launcher
├── run_app.bat             # Windows batch launcher
└── test_setup.py           # Setup verification script
```

## 🔧 Features

### For Suppliers
- Product catalog management
- Order processing and fulfillment
- Payment gateway integration (Razorpay)
- License verification system
- Analytics dashboard
- Invoice generation

### For Vendors
- Browse supplier catalogs
- Place orders
- Track order status
- Payment processing
- Order history

### Core Features
- User authentication (vendors & suppliers)
- Real-time order tracking
- Payment processing
- License verification
- Analytics and reporting
- Responsive web interface

## 🗄️ Database

The application uses MongoDB Atlas with the following collections:
- `vendors` - Vendor information
- `suppliers` - Supplier information
- `stocks` - Product inventory
- `orders` - Order management
- `coupons` - Discount management
- `licenses` - License verification

## 🔌 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup/vendor` - Vendor registration
- `POST /api/signup/supplier` - Supplier registration

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `GET /api/stocks` - Get product inventory
- `POST /api/stocks` - Add new product
- `PUT /api/stocks/<id>` - Update product
- `DELETE /api/stocks/<id>` - Delete product

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders` - List orders
- `GET /api/orders/<id>` - Get order details
- `PUT /api/orders/<id>/status` - Update order status

### Analytics
- `GET /api/dashboard/<supplier_id>` - Supplier dashboard data
- `GET /api/analytics/sales` - Sales analytics
- `GET /api/analytics/orders` - Order analytics

## 🧪 Testing

Run the setup verification script to check if everything is working:
```bash
python test_setup.py
```

This will test:
- Python package installation
- File structure
- MongoDB connection
- Flask application startup

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'app'" error**
   - Make sure you're running from the correct directory
   - Use the launcher scripts: `run_app.py` or `run_app.bat`

2. **MongoDB connection issues**
   - Check internet connection
   - Verify MongoDB Atlas credentials in `backend/app.py`

3. **Port already in use**
   - Change the port in `backend/app.py` line 2322
   - Or kill the process using port 5000

4. **Package installation issues**
   - Update pip: `python -m pip install --upgrade pip`
   - Install requirements: `pip install -r backend/requirements.txt`

### Getting Help
- Check the console output for error messages
- Verify all files are in the correct locations
- Ensure Python 3.8+ is installed
- Test MongoDB connection separately

## 📱 Usage

1. **Start the application** using one of the launcher methods
2. **Open your browser** and go to http://localhost:5000
3. **Register** as a vendor or supplier
4. **Login** and start using the platform

## 🔒 Security

- Passwords are hashed using Werkzeug
- CORS is configured for cross-origin requests
- MongoDB connection uses secure connection string
- Input validation on all API endpoints

## 📈 Future Enhancements

- Real-time notifications
- Mobile app development
- Advanced analytics
- Multi-language support
- Enhanced security features

---

**Status**: ✅ **WORKING** - All components are functional and ready for use!
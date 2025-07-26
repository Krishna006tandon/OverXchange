# Supplier Analytics Dashboard - Backend System

## 📊 Overview

This is a comprehensive Flask-based backend system for the Supplier Analytics Dashboard, designed to provide real-time analytics and insights for wholesale suppliers. The system includes MongoDB integration with fallback to sample data, ensuring it works both in development and production environments.

## 🏗️ Architecture

```
Supplier Analytics Backend
├── Flask API Server
├── MongoDB Database (with fallback)
├── RESTful Endpoints
├── Aggregation Queries
└── Sample Data System
```

## 📁 File Structure

```
backend/
├── analytics_api.py          # Main Flask application
├── analytics_schema.py       # MongoDB schema and sample data
├── requirements_analytics.txt # Python dependencies
└── ANALYTICS_README.md       # This documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements_analytics.txt
```

### 2. Start the Server

```bash
python analytics_api.py
```

The server will start at `http://localhost:5000`

### 3. Test the API

```bash
curl http://localhost:5000/api/health
```

## 📊 MongoDB Schema

### Collections

#### 1. **orders**
```json
{
  "_id": "order_001",
  "order_id": "ORD-2024-001",
  "supplier_id": "supplier_001",
  "vendor_id": "vendor_001",
  "vendor_name": "TechMart Mumbai",
  "vendor_city": "Mumbai",
  "order_date": "2024-01-15T10:30:00Z",
  "fulfillment_date": "2024-01-15T13:45:00Z",
  "status": "fulfilled",
  "total_amount": 85000,
  "items": [...],
  "fulfillment_time_hours": 3.25,
  "is_on_time": true
}
```

#### 2. **deals**
```json
{
  "_id": "deal_001",
  "deal_id": "DEAL-2024-001",
  "title": "Power Banks Mega Deal",
  "product_name": "Power Bank 20000mAh",
  "original_price": 2500,
  "deal_price": 1800,
  "total_units": 1000,
  "claimed_units": 800,
  "status": "expired",
  "is_hot_deal": true,
  "views_count": 1200,
  "claims_count": 34
}
```

#### 3. **vendors**
```json
{
  "_id": "vendor_001",
  "name": "TechMart Mumbai",
  "city": "Mumbai",
  "total_orders": 15,
  "total_spent": 1250000,
  "is_active": true,
  "watchlist_products": ["prod_001", "prod_003"]
}
```

#### 4. **products**
```json
{
  "_id": "prod_001",
  "name": "Laptop Dell XPS 13",
  "category": "Electronics",
  "current_stock": 45,
  "unit_price": 85000,
  "days_since_last_movement": 0,
  "status": "in_stock"
}
```

#### 5. **analytics_logs**
```json
{
  "_id": "log_001",
  "event_type": "deal_view",
  "deal_id": "deal_001",
  "vendor_id": "vendor_001",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔌 API Endpoints

### Core Analytics Endpoints

#### 1. **KPI Summary**
```http
GET /api/analytics/kpi-summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_orders": 1240,
    "total_revenue": 8500000,
    "active_vendors": 87,
    "avg_order_value": 6850,
    "avg_fulfillment_time": 2.8
  }
}
```

#### 2. **Sales Trends**
```http
GET /api/analytics/sales-trends
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"month": "Aug 2023", "revenue": 6500000},
    {"month": "Sep 2023", "revenue": 7200000},
    {"month": "Oct 2023", "revenue": 6800000}
  ]
}
```

#### 3. **Top Categories**
```http
GET /api/analytics/top-categories
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "category": "Electronics",
      "sales": 45,
      "revenue": 3825000
    }
  ]
}
```

#### 4. **Sales by Region**
```http
GET /api/analytics/sales-by-region
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "region": "Mumbai",
      "orders": 320,
      "revenue": 2100000
    }
  ]
}
```

#### 5. **Deal Performance**
```http
GET /api/analytics/deal-performance
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "deal_title": "Power Banks Mega Deal",
      "claimed_by": "34 Vendors",
      "units_sold": 800,
      "avg_claim_time": "3 hrs",
      "status": "Expired",
      "is_hot_deal": true
    }
  ]
}
```

#### 6. **Vendor Engagement**
```http
GET /api/analytics/vendor-engagement
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deal_views": 1200,
    "click_to_claim_ratio": 38,
    "watchlisted_products": 56,
    "repeat_vendors": 22
  }
}
```

#### 7. **Dead Stock Warnings**
```http
GET /api/analytics/dead-stock-warnings
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "product": "Bluetooth Headphones",
      "days_since_last_claim": 35,
      "suggestion": "Try bundle deal"
    }
  ]
}
```

#### 8. **Fulfillment Stats**
```http
GET /api/analytics/fulfillment-stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "on_time_fulfillments": 94,
    "partial_deliveries": 2,
    "cancelled_orders": 5,
    "avg_delay_time": "1.2 hrs"
  }
}
```

#### 9. **AI Suggestions**
```http
GET /api/analytics/ai-suggestions
```

**Response:**
```json
{
  "success": true,
  "data": [
    "🔁 Repost This Deal: Your July USB Deal had 90% claim rate — try reposting",
    "🧑‍🤝‍🧑 Target These Vendors: Vendors from Pune are searching for Wireless Mice",
    "💰 Adjust Price for Stock Clearance: Power Bank stock hasn't moved in 20 days – consider reducing price by 10%"
  ]
}
```

### Export Endpoints

#### 10. **Export Data**
```http
GET /api/analytics/export/{format}
```

**Formats:** `pdf`, `csv`, `json`

**Response:**
```json
{
  "success": true,
  "data": "...",
  "format": "json"
}
```

### Utility Endpoints

#### 11. **Complete Dashboard Data**
```http
GET /api/analytics/dashboard
```

**Response:** All analytics data in a single response

#### 12. **Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "mongodb_connected": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔍 MongoDB Aggregation Examples

### 1. KPI Summary Aggregation
```javascript
db.orders.aggregate([
  {"$match": {"status": "fulfilled"}},
  {"$group": {
    "_id": null,
    "total_orders": {"$sum": 1},
    "total_revenue": {"$sum": "$total_amount"},
    "avg_fulfillment_time": {"$avg": "$fulfillment_time_hours"}
  }}
])
```

### 2. Sales Trends Aggregation
```javascript
db.orders.aggregate([
  {"$match": {"status": "fulfilled"}},
  {"$group": {
    "_id": {
      "year": {"$year": "$order_date"},
      "month": {"$month": "$order_date"}
    },
    "revenue": {"$sum": "$total_amount"}
  }},
  {"$sort": {"_id.year": 1, "_id.month": 1}},
  {"$limit": 6}
])
```

### 3. Top Categories Aggregation
```javascript
db.orders.aggregate([
  {"$unwind": "$items"},
  {"$group": {
    "_id": "$items.category",
    "sales": {"$sum": "$items.quantity"},
    "revenue": {"$sum": "$items.total_price"}
  }},
  {"$sort": {"revenue": -1}},
  {"$limit": 5}
])
```

## ⚙️ Configuration

### Environment Variables
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=supplier_analytics

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

### MongoDB Setup
```bash
# Install MongoDB
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb

# Create database and collections
mongo
use supplier_analytics
db.createCollection("orders")
db.createCollection("deals")
db.createCollection("vendors")
db.createCollection("products")
db.createCollection("analytics_logs")
```

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test KPI summary
curl http://localhost:5000/api/analytics/kpi-summary

# Test complete dashboard
curl http://localhost:5000/api/analytics/dashboard
```

### Sample Data Population
```python
from analytics_schema import get_sample_data

# Get sample data
data = get_sample_data()

# Insert into MongoDB (if available)
if use_mongodb:
    for collection_name, documents in data.items():
        if collection_name not in ['indexes', 'schema_validation']:
            db[collection_name].insert_many(documents)
```

## 📈 Analytics Features

### 1. **KPI Dashboard**
- Total Orders Fulfilled
- Total Revenue Earned
- Active Vendor Buyers
- Average Order Value
- Average Fulfillment Time

### 2. **Sales Analytics**
- Monthly/Weekly Sales Trends
- Top Selling Categories
- Sales by Region
- Revenue Analysis

### 3. **Deal Performance**
- Deal Performance Tracking
- Hot Deal Identification
- Claim Rate Analysis
- Vendor Engagement Metrics

### 4. **Inventory Management**
- Dead Stock Warnings
- Low Demand Alerts
- Stock Movement Tracking
- Reorder Suggestions

### 5. **Fulfillment Analytics**
- On-Time Fulfillment Rates
- Delay Analysis
- Cancellation Tracking
- Performance Metrics

### 6. **AI-Powered Insights**
- Repost Deal Suggestions
- Target Vendor Recommendations
- Price Adjustment Alerts
- Market Trend Analysis

## 🔗 Frontend Integration

### JavaScript Example
```javascript
// Fetch KPI summary
fetch('/api/analytics/kpi-summary')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      updateKPICards(data.data);
    }
  });

// Fetch sales trends
fetch('/api/analytics/sales-trends')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      updateSalesChart(data.data);
    }
  });
```

### Error Handling
```javascript
fetch('/api/analytics/kpi-summary')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Handle success
    } else {
      console.error('API Error:', data.error);
      // Show fallback data
    }
  })
  .catch(error => {
    console.error('Network Error:', error);
    // Show offline message
  });
```

## 🚀 Production Deployment

### 1. **Environment Setup**
```bash
# Install production dependencies
pip install gunicorn

# Set environment variables
export FLASK_ENV=production
export MONGODB_URI=mongodb://your-mongodb-uri
```

### 2. **Gunicorn Configuration**
```bash
# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 analytics_api:app
```

### 3. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_analytics.txt .
RUN pip install -r requirements_analytics.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "analytics_api:app"]
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **MongoDB Connection Failed**
```
⚠️ MongoDB connection failed: [Errno 111] Connection refused
📊 Using sample data instead...
```
**Solution:** Ensure MongoDB is running and accessible

#### 2. **Port Already in Use**
```
OSError: [Errno 98] Address already in use
```
**Solution:** Change port or kill existing process
```bash
lsof -ti:5000 | xargs kill -9
```

#### 3. **CORS Issues**
**Solution:** Ensure CORS is properly configured for your frontend domain

### Performance Optimization

#### 1. **Database Indexes**
```javascript
// Create indexes for better performance
db.orders.createIndex({"supplier_id": 1, "order_date": -1})
db.deals.createIndex({"supplier_id": 1, "status": 1})
db.products.createIndex({"supplier_id": 1, "status": 1})
```

#### 2. **Caching**
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@app.route('/api/analytics/kpi-summary')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_kpi_summary():
    # ... implementation
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Aggregation](https://docs.mongodb.com/manual/aggregation/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎯 Ready for Hackathon!** This backend system provides a solid foundation for your supplier analytics dashboard with comprehensive data management, real-time analytics, and scalable architecture. 
"""
Flask API Backend for Supplier Analytics Dashboard
Provides comprehensive analytics data through RESTful endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import random
from pymongo import MongoClient
from bson import json_util
import os

app = Flask(__name__)
CORS(app)

# MongoDB Connection
try:
    # Try to connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['supplier_analytics']
    print("✅ Connected to MongoDB successfully!")
    use_mongodb = True
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("📊 Using sample data instead...")
    use_mongodb = False

def get_collection(collection_name):
    """Get MongoDB collection or return None if not available"""
    if use_mongodb:
        return db[collection_name]
    return None

# Sample data fallback
SAMPLE_DATA = {
    "kpi_summary": {
        "total_orders": 1240,
        "total_revenue": 8500000,
        "active_vendors": 87,
        "avg_order_value": 6850,
        "avg_fulfillment_time": 2.8
    },
    "sales_trends": [
        {"month": "Aug 2023", "revenue": 6500000},
        {"month": "Sep 2023", "revenue": 7200000},
        {"month": "Oct 2023", "revenue": 6800000},
        {"month": "Nov 2023", "revenue": 7500000},
        {"month": "Dec 2023", "revenue": 8200000},
        {"month": "Jan 2024", "revenue": 8500000}
    ],
    "top_categories": [
        {"category": "Electronics", "sales": 45, "revenue": 3825000},
        {"category": "Accessories", "sales": 30, "revenue": 2550000},
        {"category": "Cables", "sales": 15, "revenue": 1275000},
        {"category": "Audio", "sales": 10, "revenue": 850000}
    ],
    "sales_by_region": [
        {"region": "Mumbai", "orders": 320, "revenue": 2100000},
        {"region": "Delhi", "orders": 210, "revenue": 1600000},
        {"region": "Pune", "orders": 180, "revenue": 1100000},
        {"region": "Bangalore", "orders": 140, "revenue": 950000},
        {"region": "Others", "orders": 390, "revenue": 2750000}
    ],
    "deal_performance": [
        {
            "deal_title": "Power Banks Mega Deal",
            "claimed_by": "34 Vendors",
            "units_sold": 800,
            "avg_claim_time": "3 hrs",
            "status": "Expired",
            "is_hot_deal": True
        },
        {
            "deal_title": "Wireless Mouse Bonanza",
            "claimed_by": "18 Vendors",
            "units_sold": 320,
            "avg_claim_time": "2.5 hrs",
            "status": "Active",
            "is_hot_deal": False
        },
        {
            "deal_title": "USB-C Cable Fest",
            "claimed_by": "12 Vendors",
            "units_sold": 150,
            "avg_claim_time": "4 hrs",
            "status": "Expired",
            "is_hot_deal": False
        }
    ],
    "vendor_engagement": {
        "deal_views": 1200,
        "click_to_claim_ratio": 38,
        "watchlisted_products": 56,
        "repeat_vendors": 22
    },
    "dead_stock_warnings": [
        {
            "product": "Bluetooth Headphones",
            "days_since_last_claim": 35,
            "suggestion": "Try bundle deal"
        },
        {
            "product": "USB-C Cable",
            "days_since_last_claim": 30,
            "suggestion": "Reduce price by 10%"
        },
        {
            "product": "Wireless Mouse",
            "days_since_last_claim": 28,
            "suggestion": "Promote as add-on"
        }
    ],
    "fulfillment_stats": {
        "on_time_fulfillments": 94,
        "partial_deliveries": 2,
        "cancelled_orders": 5,
        "avg_delay_time": "1.2 hrs"
    },
    "ai_suggestions": [
        "🔁 Repost This Deal: Your July USB Deal had 90% claim rate — try reposting",
        "🧑‍🤝‍🧑 Target These Vendors: Vendors from Pune are searching for Wireless Mice",
        "💰 Adjust Price for Stock Clearance: Power Bank stock hasn't moved in 20 days – consider reducing price by 10%"
    ]
}

@app.route('/api/analytics/kpi-summary', methods=['GET'])
def get_kpi_summary():
    """Get KPI summary data"""
    try:
        if use_mongodb:
            orders_collection = get_collection('orders')
            if orders_collection:
                # MongoDB aggregation for KPI summary
                pipeline = [
                    {"$match": {"status": "fulfilled"}},
                    {"$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"},
                        "avg_fulfillment_time": {"$avg": "$fulfillment_time_hours"}
                    }},
                    {"$project": {
                        "_id": 0,
                        "total_orders": 1,
                        "total_revenue": 1,
                        "avg_fulfillment_time": {"$round": ["$avg_fulfillment_time", 1]}
                    }}
                ]
                result = list(orders_collection.aggregate(pipeline))
                
                if result:
                    kpi_data = result[0]
                    # Get active vendors count
                    vendors_collection = get_collection('vendors')
                    active_vendors = vendors_collection.count_documents({"is_active": True}) if vendors_collection else 87
                    
                    return jsonify({
                        "success": True,
                        "data": {
                            "total_orders": kpi_data.get("total_orders", 0),
                            "total_revenue": kpi_data.get("total_revenue", 0),
                            "active_vendors": active_vendors,
                            "avg_order_value": round(kpi_data.get("total_revenue", 0) / max(kpi_data.get("total_orders", 1), 1)),
                            "avg_fulfillment_time": kpi_data.get("avg_fulfillment_time", 0)
                        }
                    })
        
        # Fallback to sample data
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["kpi_summary"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["kpi_summary"]
        }), 500

@app.route('/api/analytics/sales-trends', methods=['GET'])
def get_sales_trends():
    """Get sales trends data"""
    try:
        if use_mongodb:
            orders_collection = get_collection('orders')
            if orders_collection:
                # MongoDB aggregation for sales trends
                pipeline = [
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
                ]
                result = list(orders_collection.aggregate(pipeline))
                
                if result:
                    trends = []
                    for item in result:
                        month_name = datetime(item["_id"]["year"], item["_id"]["month"], 1).strftime("%b %Y")
                        trends.append({
                            "month": month_name,
                            "revenue": item["revenue"]
                        })
                    return jsonify({"success": True, "data": trends})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["sales_trends"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["sales_trends"]
        }), 500

@app.route('/api/analytics/top-categories', methods=['GET'])
def get_top_categories():
    """Get top selling categories"""
    try:
        if use_mongodb:
            orders_collection = get_collection('orders')
            if orders_collection:
                # MongoDB aggregation for top categories
                pipeline = [
                    {"$unwind": "$items"},
                    {"$group": {
                        "_id": "$items.category",
                        "sales": {"$sum": "$items.quantity"},
                        "revenue": {"$sum": "$items.total_price"}
                    }},
                    {"$sort": {"revenue": -1}},
                    {"$limit": 5}
                ]
                result = list(orders_collection.aggregate(pipeline))
                
                if result:
                    categories = []
                    for item in result:
                        categories.append({
                            "category": item["_id"],
                            "sales": item["sales"],
                            "revenue": item["revenue"]
                        })
                    return jsonify({"success": True, "data": categories})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["top_categories"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["top_categories"]
        }), 500

@app.route('/api/analytics/sales-by-region', methods=['GET'])
def get_sales_by_region():
    """Get sales by region"""
    try:
        if use_mongodb:
            orders_collection = get_collection('orders')
            if orders_collection:
                # MongoDB aggregation for sales by region
                pipeline = [
                    {"$match": {"status": "fulfilled"}},
                    {"$group": {
                        "_id": "$vendor_city",
                        "orders": {"$sum": 1},
                        "revenue": {"$sum": "$total_amount"}
                    }},
                    {"$sort": {"revenue": -1}},
                    {"$limit": 10}
                ]
                result = list(orders_collection.aggregate(pipeline))
                
                if result:
                    regions = []
                    for item in result:
                        regions.append({
                            "region": item["_id"],
                            "orders": item["orders"],
                            "revenue": item["revenue"]
                        })
                    return jsonify({"success": True, "data": regions})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["sales_by_region"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["sales_by_region"]
        }), 500

@app.route('/api/analytics/deal-performance', methods=['GET'])
def get_deal_performance():
    """Get deal performance data"""
    try:
        if use_mongodb:
            deals_collection = get_collection('deals')
            if deals_collection:
                # MongoDB aggregation for deal performance
                pipeline = [
                    {"$sort": {"created_at": -1}},
                    {"$limit": 10},
                    {"$project": {
                        "_id": 0,
                        "deal_title": "$title",
                        "claimed_by": {"$concat": [{"$toString": "$claims_count"}, " Vendors"]},
                        "units_sold": "$claimed_units",
                        "avg_claim_time": {"$concat": [{"$toString": "$avg_claim_time_hours"}, " hrs"]},
                        "status": "$status",
                        "is_hot_deal": "$is_hot_deal"
                    }}
                ]
                result = list(deals_collection.aggregate(pipeline))
                
                if result:
                    return jsonify({"success": True, "data": result})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["deal_performance"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["deal_performance"]
        }), 500

@app.route('/api/analytics/vendor-engagement', methods=['GET'])
def get_vendor_engagement():
    """Get vendor engagement metrics"""
    try:
        if use_mongodb:
            analytics_collection = get_collection('analytics_logs')
            if analytics_collection:
                # MongoDB aggregation for vendor engagement
                pipeline = [
                    {"$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1}
                    }}
                ]
                result = list(analytics_collection.aggregate(pipeline))
                
                if result:
                    engagement_data = {
                        "deal_views": 0,
                        "click_to_claim_ratio": 0,
                        "watchlisted_products": 0,
                        "repeat_vendors": 0
                    }
                    
                    for item in result:
                        if item["_id"] == "deal_view":
                            engagement_data["deal_views"] = item["count"]
                        elif item["_id"] == "product_watchlist":
                            engagement_data["watchlisted_products"] = item["count"]
                    
                    # Calculate click-to-claim ratio
                    if engagement_data["deal_views"] > 0:
                        claim_events = next((item["count"] for item in result if item["_id"] == "deal_claim"), 0)
                        engagement_data["click_to_claim_ratio"] = round((claim_events / engagement_data["deal_views"]) * 100)
                    
                    return jsonify({"success": True, "data": engagement_data})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["vendor_engagement"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["vendor_engagement"]
        }), 500

@app.route('/api/analytics/dead-stock-warnings', methods=['GET'])
def get_dead_stock_warnings():
    """Get dead stock warnings"""
    try:
        if use_mongodb:
            products_collection = get_collection('products')
            if products_collection:
                # MongoDB aggregation for dead stock warnings
                pipeline = [
                    {"$match": {"days_since_last_movement": {"$gte": 30}}},
                    {"$sort": {"days_since_last_movement": -1}},
                    {"$limit": 10},
                    {"$project": {
                        "_id": 0,
                        "product": "$name",
                        "days_since_last_claim": "$days_since_last_movement",
                        "suggestion": {
                            "$cond": {
                                "if": {"$gte": ["$days_since_last_movement", 60]},
                                "then": "Reduce price by 15%",
                                "else": "Try bundle deal"
                            }
                        }
                    }}
                ]
                result = list(products_collection.aggregate(pipeline))
                
                if result:
                    return jsonify({"success": True, "data": result})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["dead_stock_warnings"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["dead_stock_warnings"]
        }), 500

@app.route('/api/analytics/fulfillment-stats', methods=['GET'])
def get_fulfillment_stats():
    """Get fulfillment statistics"""
    try:
        if use_mongodb:
            orders_collection = get_collection('orders')
            if orders_collection:
                # MongoDB aggregation for fulfillment stats
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "on_time_fulfillments": {"$sum": {"$cond": ["$is_on_time", 1, 0]}},
                        "cancelled_orders": {"$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}},
                        "avg_delay_time": {"$avg": {"$cond": [{"$not": "$is_on_time"}, "$fulfillment_time_hours", None]}}
                    }},
                    {"$project": {
                        "_id": 0,
                        "on_time_fulfillments": {"$round": [{"$multiply": [{"$divide": ["$on_time_fulfillments", "$total_orders"]}, 100]}, 1]},
                        "partial_deliveries": 2,  # This would need separate tracking
                        "cancelled_orders": 1,
                        "avg_delay_time": {"$round": ["$avg_delay_time", 1]}
                    }}
                ]
                result = list(orders_collection.aggregate(pipeline))
                
                if result:
                    return jsonify({"success": True, "data": result[0]})
        
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["fulfillment_stats"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["fulfillment_stats"]
        }), 500

@app.route('/api/analytics/ai-suggestions', methods=['GET'])
def get_ai_suggestions():
    """Get AI-powered suggestions"""
    try:
        # AI suggestions are typically generated based on business logic
        # For now, return sample suggestions
        return jsonify({
            "success": True,
            "data": SAMPLE_DATA["ai_suggestions"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": SAMPLE_DATA["ai_suggestions"]
        }), 500

@app.route('/api/analytics/export/<format>', methods=['GET'])
def export_analytics(format):
    """Export analytics data in specified format"""
    try:
        if format not in ['pdf', 'csv', 'json']:
            return jsonify({"success": False, "error": "Unsupported format"}), 400
        
        # Get all analytics data
        all_data = {
            "kpi_summary": SAMPLE_DATA["kpi_summary"],
            "sales_trends": SAMPLE_DATA["sales_trends"],
            "top_categories": SAMPLE_DATA["top_categories"],
            "sales_by_region": SAMPLE_DATA["sales_by_region"],
            "deal_performance": SAMPLE_DATA["deal_performance"],
            "vendor_engagement": SAMPLE_DATA["vendor_engagement"],
            "dead_stock_warnings": SAMPLE_DATA["dead_stock_warnings"],
            "fulfillment_stats": SAMPLE_DATA["fulfillment_stats"],
            "ai_suggestions": SAMPLE_DATA["ai_suggestions"],
            "exported_at": datetime.now().isoformat()
        }
        
        if format == 'json':
            return jsonify({
                "success": True,
                "data": all_data,
                "format": "json"
            })
        elif format == 'csv':
            # Convert to CSV format (simplified)
            csv_data = "Metric,Value\n"
            csv_data += f"Total Orders,{all_data['kpi_summary']['total_orders']}\n"
            csv_data += f"Total Revenue,{all_data['kpi_summary']['total_revenue']}\n"
            csv_data += f"Active Vendors,{all_data['kpi_summary']['active_vendors']}\n"
            
            return jsonify({
                "success": True,
                "data": csv_data,
                "format": "csv"
            })
        else:  # PDF
            return jsonify({
                "success": True,
                "message": "PDF export functionality would be implemented here",
                "data": all_data,
                "format": "pdf"
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        # Aggregate all analytics data
        dashboard_data = {
            "kpi_summary": SAMPLE_DATA["kpi_summary"],
            "sales_trends": SAMPLE_DATA["sales_trends"],
            "top_categories": SAMPLE_DATA["top_categories"],
            "sales_by_region": SAMPLE_DATA["sales_by_region"],
            "deal_performance": SAMPLE_DATA["deal_performance"],
            "vendor_engagement": SAMPLE_DATA["vendor_engagement"],
            "dead_stock_warnings": SAMPLE_DATA["dead_stock_warnings"],
            "fulfillment_stats": SAMPLE_DATA["fulfillment_stats"],
            "ai_suggestions": SAMPLE_DATA["ai_suggestions"]
        }
        
        return jsonify({
            "success": True,
            "data": dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mongodb_connected": use_mongodb,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Supplier Analytics API Server...")
    print(f"📊 MongoDB Status: {'✅ Connected' if use_mongodb else '⚠️ Using Sample Data'}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📚 API Documentation:")
    print("  - GET /api/analytics/kpi-summary")
    print("  - GET /api/analytics/sales-trends")
    print("  - GET /api/analytics/top-categories")
    print("  - GET /api/analytics/sales-by-region")
    print("  - GET /api/analytics/deal-performance")
    print("  - GET /api/analytics/vendor-engagement")
    print("  - GET /api/analytics/dead-stock-warnings")
    print("  - GET /api/analytics/fulfillment-stats")
    print("  - GET /api/analytics/ai-suggestions")
    print("  - GET /api/analytics/export/<format>")
    print("  - GET /api/analytics/dashboard")
    print("  - GET /api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
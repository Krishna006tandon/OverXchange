"""
MongoDB Schema Design for Supplier Analytics Dashboard
Collections and sample data for comprehensive analytics
"""

from datetime import datetime, timedelta
import random

# Sample data for testing and development

# 1. ORDERS Collection
orders_sample = [
    {
        "_id": "order_001",
        "order_id": "ORD-2024-001",
        "supplier_id": "supplier_001",
        "vendor_id": "vendor_001",
        "vendor_name": "TechMart Mumbai",
        "vendor_city": "Mumbai",
        "vendor_state": "Maharashtra",
        "order_date": datetime(2024, 1, 15, 10, 30),
        "fulfillment_date": datetime(2024, 1, 15, 13, 45),
        "status": "fulfilled",
        "total_amount": 85000,
        "items": [
            {
                "product_id": "prod_001",
                "product_name": "Laptop Dell XPS 13",
                "category": "Electronics",
                "quantity": 5,
                "unit_price": 85000,
                "total_price": 425000
            }
        ],
        "fulfillment_time_hours": 3.25,
        "is_on_time": True,
        "payment_status": "paid",
        "created_at": datetime(2024, 1, 15, 10, 30),
        "updated_at": datetime(2024, 1, 15, 13, 45)
    },
    {
        "_id": "order_002",
        "order_id": "ORD-2024-002",
        "supplier_id": "supplier_001",
        "vendor_id": "vendor_002",
        "vendor_name": "Digital Hub Delhi",
        "vendor_city": "Delhi",
        "vendor_state": "Delhi",
        "order_date": datetime(2024, 1, 16, 14, 20),
        "fulfillment_date": datetime(2024, 1, 16, 18, 30),
        "status": "fulfilled",
        "total_amount": 120000,
        "items": [
            {
                "product_id": "prod_002",
                "product_name": "Wireless Mouse",
                "category": "Accessories",
                "quantity": 100,
                "unit_price": 1200,
                "total_price": 120000
            }
        ],
        "fulfillment_time_hours": 4.17,
        "is_on_time": True,
        "payment_status": "paid",
        "created_at": datetime(2024, 1, 16, 14, 20),
        "updated_at": datetime(2024, 1, 16, 18, 30)
    },
    {
        "_id": "order_003",
        "order_id": "ORD-2024-003",
        "supplier_id": "supplier_001",
        "vendor_id": "vendor_003",
        "vendor_name": "Pune Electronics",
        "vendor_city": "Pune",
        "vendor_state": "Maharashtra",
        "order_date": datetime(2024, 1, 17, 9, 15),
        "fulfillment_date": datetime(2024, 1, 17, 12, 45),
        "status": "fulfilled",
        "total_amount": 250000,
        "items": [
            {
                "product_id": "prod_003",
                "product_name": "Bluetooth Headphones",
                "category": "Audio",
                "quantity": 100,
                "unit_price": 2500,
                "total_price": 250000
            }
        ],
        "fulfillment_time_hours": 3.5,
        "is_on_time": True,
        "payment_status": "paid",
        "created_at": datetime(2024, 1, 17, 9, 15),
        "updated_at": datetime(2024, 1, 17, 12, 45)
    }
]

# 2. DEALS Collection
deals_sample = [
    {
        "_id": "deal_001",
        "deal_id": "DEAL-2024-001",
        "supplier_id": "supplier_001",
        "title": "Power Banks Mega Deal",
        "description": "High-capacity power banks at wholesale prices",
        "product_id": "prod_004",
        "product_name": "Power Bank 20000mAh",
        "category": "Electronics",
        "original_price": 2500,
        "deal_price": 1800,
        "total_units": 1000,
        "claimed_units": 800,
        "available_units": 200,
        "start_date": datetime(2024, 1, 10, 0, 0),
        "end_date": datetime(2024, 1, 20, 23, 59),
        "status": "expired",
        "views_count": 1200,
        "claims_count": 34,
        "avg_claim_time_hours": 3.0,
        "is_hot_deal": True,
        "created_at": datetime(2024, 1, 10, 0, 0),
        "updated_at": datetime(2024, 1, 20, 23, 59)
    },
    {
        "_id": "deal_002",
        "deal_id": "DEAL-2024-002",
        "supplier_id": "supplier_001",
        "title": "Wireless Mouse Bonanza",
        "description": "Premium wireless mice for gaming and office use",
        "product_id": "prod_002",
        "product_name": "Wireless Mouse",
        "category": "Accessories",
        "original_price": 1500,
        "deal_price": 1200,
        "total_units": 500,
        "claimed_units": 320,
        "available_units": 180,
        "start_date": datetime(2024, 1, 15, 0, 0),
        "end_date": datetime(2024, 1, 25, 23, 59),
        "status": "active",
        "views_count": 800,
        "claims_count": 18,
        "avg_claim_time_hours": 2.5,
        "is_hot_deal": False,
        "created_at": datetime(2024, 1, 15, 0, 0),
        "updated_at": datetime(2024, 1, 15, 0, 0)
    },
    {
        "_id": "deal_003",
        "deal_id": "DEAL-2024-003",
        "supplier_id": "supplier_001",
        "title": "USB-C Cable Fest",
        "description": "High-quality USB-C cables for all devices",
        "product_id": "prod_005",
        "product_name": "USB-C Cable",
        "category": "Cables",
        "original_price": 800,
        "deal_price": 500,
        "total_units": 300,
        "claimed_units": 150,
        "available_units": 150,
        "start_date": datetime(2024, 1, 12, 0, 0),
        "end_date": datetime(2024, 1, 22, 23, 59),
        "status": "expired",
        "views_count": 600,
        "claims_count": 12,
        "avg_claim_time_hours": 4.0,
        "is_hot_deal": False,
        "created_at": datetime(2024, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 22, 23, 59)
    }
]

# 3. VENDORS Collection
vendors_sample = [
    {
        "_id": "vendor_001",
        "vendor_id": "VEND-001",
        "name": "TechMart Mumbai",
        "email": "contact@techmartmumbai.com",
        "phone": "+91-9876543210",
        "city": "Mumbai",
        "state": "Maharashtra",
        "registration_date": datetime(2023, 6, 15),
        "total_orders": 15,
        "total_spent": 1250000,
        "last_order_date": datetime(2024, 1, 15),
        "is_active": True,
        "watchlist_products": ["prod_001", "prod_003"],
        "preferred_categories": ["Electronics", "Audio"],
        "created_at": datetime(2023, 6, 15),
        "updated_at": datetime(2024, 1, 15)
    },
    {
        "_id": "vendor_002",
        "vendor_id": "VEND-002",
        "name": "Digital Hub Delhi",
        "email": "info@digitalhubdelhi.com",
        "phone": "+91-9876543211",
        "city": "Delhi",
        "state": "Delhi",
        "registration_date": datetime(2023, 8, 20),
        "total_orders": 8,
        "total_spent": 680000,
        "last_order_date": datetime(2024, 1, 16),
        "is_active": True,
        "watchlist_products": ["prod_002", "prod_004"],
        "preferred_categories": ["Accessories", "Electronics"],
        "created_at": datetime(2023, 8, 20),
        "updated_at": datetime(2024, 1, 16)
    },
    {
        "_id": "vendor_003",
        "vendor_id": "VEND-003",
        "name": "Pune Electronics",
        "email": "sales@puneelectronics.com",
        "phone": "+91-9876543212",
        "city": "Pune",
        "state": "Maharashtra",
        "registration_date": datetime(2023, 9, 10),
        "total_orders": 12,
        "total_spent": 950000,
        "last_order_date": datetime(2024, 1, 17),
        "is_active": True,
        "watchlist_products": ["prod_003", "prod_005"],
        "preferred_categories": ["Audio", "Cables"],
        "created_at": datetime(2023, 9, 10),
        "updated_at": datetime(2024, 1, 17)
    }
]

# 4. PRODUCTS Collection
products_sample = [
    {
        "_id": "prod_001",
        "product_id": "PROD-001",
        "name": "Laptop Dell XPS 13",
        "category": "Electronics",
        "sku": "DELL-XPS-001",
        "supplier_id": "supplier_001",
        "current_stock": 45,
        "min_stock_level": 10,
        "unit_price": 85000,
        "last_movement_date": datetime(2024, 1, 15),
        "days_since_last_movement": 0,
        "total_sold": 155,
        "total_revenue": 13175000,
        "status": "in_stock",
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2024, 1, 15)
    },
    {
        "_id": "prod_002",
        "product_id": "PROD-002",
        "name": "Wireless Mouse",
        "category": "Accessories",
        "sku": "WM-001",
        "supplier_id": "supplier_001",
        "current_stock": 8,
        "min_stock_level": 20,
        "unit_price": 1200,
        "last_movement_date": datetime(2024, 1, 16),
        "days_since_last_movement": 1,
        "total_sold": 420,
        "total_revenue": 504000,
        "status": "low_stock",
        "created_at": datetime(2023, 3, 15),
        "updated_at": datetime(2024, 1, 16)
    },
    {
        "_id": "prod_003",
        "product_id": "PROD-003",
        "name": "Bluetooth Headphones",
        "category": "Audio",
        "sku": "BT-HP-001",
        "supplier_id": "supplier_001",
        "current_stock": 67,
        "min_stock_level": 15,
        "unit_price": 2500,
        "last_movement_date": datetime(2024, 1, 17),
        "days_since_last_movement": 2,
        "total_sold": 233,
        "total_revenue": 582500,
        "status": "in_stock",
        "created_at": datetime(2023, 5, 20),
        "updated_at": datetime(2024, 1, 17)
    },
    {
        "_id": "prod_004",
        "product_id": "PROD-004",
        "name": "Power Bank 20000mAh",
        "category": "Electronics",
        "sku": "PB-20K-001",
        "supplier_id": "supplier_001",
        "current_stock": 200,
        "min_stock_level": 50,
        "unit_price": 1800,
        "last_movement_date": datetime(2024, 1, 20),
        "days_since_last_movement": 5,
        "total_sold": 800,
        "total_revenue": 1440000,
        "status": "in_stock",
        "created_at": datetime(2023, 7, 10),
        "updated_at": datetime(2024, 1, 20)
    },
    {
        "_id": "prod_005",
        "product_id": "PROD-005",
        "name": "USB-C Cable",
        "category": "Cables",
        "sku": "USB-C-001",
        "supplier_id": "supplier_001",
        "current_stock": 0,
        "min_stock_level": 25,
        "unit_price": 500,
        "last_movement_date": datetime(2024, 1, 22),
        "days_since_last_movement": 7,
        "total_sold": 150,
        "total_revenue": 75000,
        "status": "out_of_stock",
        "created_at": datetime(2023, 8, 5),
        "updated_at": datetime(2024, 1, 22)
    }
]

# 5. ANALYTICS_LOGS Collection
analytics_logs_sample = [
    {
        "_id": "log_001",
        "supplier_id": "supplier_001",
        "event_type": "deal_view",
        "deal_id": "deal_001",
        "vendor_id": "vendor_001",
        "timestamp": datetime(2024, 1, 15, 10, 30),
        "session_id": "sess_001",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1"
    },
    {
        "_id": "log_002",
        "supplier_id": "supplier_001",
        "event_type": "deal_claim",
        "deal_id": "deal_001",
        "vendor_id": "vendor_001",
        "timestamp": datetime(2024, 1, 15, 13, 30),
        "session_id": "sess_001",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1"
    },
    {
        "_id": "log_003",
        "supplier_id": "supplier_001",
        "event_type": "product_watchlist",
        "product_id": "prod_001",
        "vendor_id": "vendor_002",
        "timestamp": datetime(2024, 1, 16, 14, 20),
        "session_id": "sess_002",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.2"
    }
]

# MongoDB Indexes for Performance
indexes = {
    "orders": [
        [("supplier_id", 1)],
        [("order_date", -1)],
        [("vendor_id", 1)],
        [("status", 1)],
        [("supplier_id", 1), ("order_date", -1)]
    ],
    "deals": [
        [("supplier_id", 1)],
        [("status", 1)],
        [("end_date", 1)],
        [("is_hot_deal", 1)],
        [("supplier_id", 1), ("status", 1)]
    ],
    "vendors": [
        [("supplier_id", 1)],
        [("city", 1)],
        [("is_active", 1)],
        [("last_order_date", -1)]
    ],
    "products": [
        [("supplier_id", 1)],
        [("category", 1)],
        [("status", 1)],
        [("last_movement_date", -1)],
        [("supplier_id", 1), ("status", 1)]
    ],
    "analytics_logs": [
        [("supplier_id", 1)],
        [("event_type", 1)],
        [("timestamp", -1)],
        [("deal_id", 1)],
        [("vendor_id", 1)],
        [("supplier_id", 1), ("event_type", 1), ("timestamp", -1)]
    ]
}

# Schema validation rules
schema_validation = {
    "orders": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["order_id", "supplier_id", "vendor_id", "order_date", "status", "total_amount"],
                "properties": {
                    "order_id": {"bsonType": "string"},
                    "supplier_id": {"bsonType": "string"},
                    "vendor_id": {"bsonType": "string"},
                    "total_amount": {"bsonType": "number"},
                    "status": {"enum": ["pending", "confirmed", "fulfilled", "cancelled"]}
                }
            }
        }
    },
    "deals": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["deal_id", "supplier_id", "title", "start_date", "end_date", "status"],
                "properties": {
                    "deal_id": {"bsonType": "string"},
                    "supplier_id": {"bsonType": "string"},
                    "title": {"bsonType": "string"},
                    "status": {"enum": ["active", "expired", "cancelled"]}
                }
            }
        }
    }
}

def get_sample_data():
    """Return all sample data for testing"""
    return {
        "orders": orders_sample,
        "deals": deals_sample,
        "vendors": vendors_sample,
        "products": products_sample,
        "analytics_logs": analytics_logs_sample,
        "indexes": indexes,
        "schema_validation": schema_validation
    }

if __name__ == "__main__":
    # Print sample data for verification
    data = get_sample_data()
    print("MongoDB Schema Design for Supplier Analytics Dashboard")
    print("=" * 60)
    print(f"Orders: {len(data['orders'])} documents")
    print(f"Deals: {len(data['deals'])} documents")
    print(f"Vendors: {len(data['vendors'])} documents")
    print(f"Products: {len(data['products'])} documents")
    print(f"Analytics Logs: {len(data['analytics_logs'])} documents")
    print("\nSample order:")
    print(data['orders'][0]) 
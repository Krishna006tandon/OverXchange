#!/usr/bin/env python3
"""
Test script to create a sample order for testing order accept functionality
"""

import requests
import json
from datetime import datetime

# Railway app URL
BASE_URL = "https://overxchange-production.up.railway.app"

def create_test_order():
    """Create a test order for debugging"""
    
    order_data = {
        "customerInfo": {
            "firstName": "Test",
            "lastName": "Vendor",
            "email": "test@vendor.com",
            "phone": "1234567890"
        },
        "shippingAddress": {
            "addressLine1": "123 Test Street",
            "addressLine2": "Test Area",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postalCode": "400001"
        },
        "shippingMethod": "standard",
        "deliveryInstructions": "Test delivery",
        "paymentMethod": "cod",
        "items": [
            {
                "name": "Test Item 1",
                "quantity": 5,
                "price": 100,
                "supplierName": "ND Hotel",
                "supplierId": "688537c9b69abf0009982a2d"
            },
            {
                "name": "Test Item 2", 
                "quantity": 3,
                "price": 150,
                "supplierName": "dosa wala",
                "supplierId": "68853ece7456697566783cb0"
            }
        ],
        "subtotal": 950,
        "shippingCost": 50,
        "taxAmount": 95,
        "totalAmount": 1095,
        "vendor_id": "test_vendor_123"
    }
    
    try:
        print("Creating test order...")
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order created successfully!")
            print(f"Order ID: {result.get('order_id')}")
            print(f"MongoDB ID: {result.get('order_mongo_id')}")
            return result.get('order_id')
        else:
            print(f"❌ Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return None

def test_order_accept(order_id):
    """Test order accept functionality"""
    
    if not order_id:
        print("❌ No order ID to test")
        return
    
    accept_data = {
        "supplier_name": "ND Hotel",
        "acceptance_notes": "Test acceptance",
        "estimated_delivery": "2025-07-30"
    }
    
    try:
        print(f"\nTesting order accept for: {order_id}")
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/accept", json=accept_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Order accept successful!")
        else:
            print("❌ Order accept failed!")
            
    except Exception as e:
        print(f"❌ Error testing order accept: {e}")

def list_all_orders():
    """List all orders in database"""
    
    try:
        print("\nListing all orders...")
        response = requests.get(f"{BASE_URL}/api/orders")
        
        if response.status_code == 200:
            result = response.json()
            orders = result.get('orders', [])
            print(f"Total orders: {len(orders)}")
            
            for order in orders:
                print(f"- {order.get('order_id')} - {order.get('status')}")
        else:
            print(f"❌ Failed to list orders: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing orders: {e}")

if __name__ == "__main__":
    print("🚀 OverXchange Order Testing")
    print("=" * 50)
    
    # List existing orders
    list_all_orders()
    
    # Create test order
    order_id = create_test_order()
    
    # Test order accept
    if order_id:
        test_order_accept(order_id)
    
    print("\n✅ Testing completed!") 
#!/usr/bin/env python3
"""
Test script to test order accept with specific order ID
"""

import requests
import json

# Railway app URL
BASE_URL = "https://overxchange-production.up.railway.app"

def test_specific_order_accept(order_id):
    """Test order accept for a specific order ID"""
    
    accept_data = {
        "supplier_name": "ND Hotel",
        "acceptance_notes": "Test acceptance for specific order",
        "estimated_delivery": "2025-07-30"
    }
    
    try:
        print(f"Testing order accept for: {order_id}")
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/accept", json=accept_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Order accept successful!")
            return True
        else:
            print("❌ Order accept failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing order accept: {e}")
        return False

def test_multiple_orders():
    """Test multiple order IDs"""
    
    # Test with the order ID that was failing
    failing_order_id = "ORD-20250727-F66531"
    print(f"Testing failing order ID: {failing_order_id}")
    test_specific_order_accept(failing_order_id)
    
    print("\n" + "="*50)
    
    # Test with the order ID we created
    working_order_id = "ORD-20250727-F6383B"
    print(f"Testing working order ID: {working_order_id}")
    test_specific_order_accept(working_order_id)

if __name__ == "__main__":
    print("🚀 Testing Specific Order Accept")
    print("=" * 50)
    
    test_multiple_orders()
    
    print("\n✅ Testing completed!") 
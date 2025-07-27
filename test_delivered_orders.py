#!/usr/bin/env python3
"""
Test script to fetch delivered orders statistics from the backend
"""

import requests
import json

def test_delivered_orders_stats():
    """Test the delivered orders stats API endpoint"""
    
    # Base URL - change this to your backend URL
    base_url = "http://localhost:5000"
    
    # Test with a sample supplier ID (you'll need to replace this with a real supplier ID)
    supplier_id = "supplier123"  # Replace with actual supplier ID from your database
    
    try:
        # Make API call to get delivered orders stats
        response = requests.get(f"{base_url}/api/orders/delivered-stats/{supplier_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                stats = data['stats']
                supplier_name = data['supplier_name']
                
                print("=" * 60)
                print(f"📊 DELIVERED ORDERS STATISTICS FOR: {supplier_name}")
                print("=" * 60)
                print(f"📦 Total Orders: {stats['total_orders']}")
                print(f"✅ Delivered Orders: {stats['delivered_orders']}")
                print(f"⏳ Remaining Orders: {stats['remaining_orders']}")
                print(f"🔄 Pending Orders: {stats['pending_orders']}")
                print(f"❌ Rejected Orders: {stats['rejected_orders']}")
                print(f"💰 Total Delivered Value: ₹{stats['total_delivered_value']:.2f}")
                print(f"📈 Delivery Rate: {stats['delivery_rate']}%")
                print("=" * 60)
                
                # Calculate and show the breakdown
                print("\n📋 ORDER BREAKDOWN:")
                print(f"   • Delivered: {stats['delivered_orders']} orders")
                print(f"   • Pending: {stats['pending_orders']} orders")
                print(f"   • Rejected: {stats['rejected_orders']} orders")
                print(f"   • Total: {stats['total_orders']} orders")
                
                print(f"\n🎯 REMAINING ORDERS TO DELIVER: {stats['remaining_orders']}")
                
                if stats['total_orders'] > 0:
                    completion_percentage = (stats['delivered_orders'] / stats['total_orders']) * 100
                    print(f"📊 COMPLETION: {completion_percentage:.1f}%")
                else:
                    print("📊 COMPLETION: No orders yet")
                    
            else:
                print(f"❌ Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_with_real_supplier_id():
    """Test with a real supplier ID from the database"""
    
    base_url = "http://localhost:5000"
    
    try:
        # First, get all suppliers to find a real supplier ID
        response = requests.get(f"{base_url}/api/suppliers")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success'] and data['suppliers']:
                # Use the first supplier's ID
                supplier = data['suppliers'][0]
                supplier_id = supplier['_id']
                supplier_name = supplier.get('business_name', supplier.get('name', 'Unknown'))
                
                print(f"🔍 Testing with supplier: {supplier_name} (ID: {supplier_id})")
                print("-" * 60)
                
                # Now test the delivered orders stats
                stats_response = requests.get(f"{base_url}/api/orders/delivered-stats/{supplier_id}")
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    
                    if stats_data['success']:
                        stats = stats_data['stats']
                        
                        print(f"📦 Total Orders: {stats['total_orders']}")
                        print(f"✅ Delivered: {stats['delivered_orders']}")
                        print(f"⏳ Remaining: {stats['remaining_orders']}")
                        print(f"📈 Delivery Rate: {stats['delivery_rate']}%")
                        print(f"💰 Total Value: ₹{stats['total_delivered_value']:.2f}")
                    else:
                        print(f"❌ Error: {stats_data['message']}")
                else:
                    print(f"❌ Stats API Error: {stats_response.status_code}")
            else:
                print("❌ No suppliers found in database")
        else:
            print(f"❌ Error fetching suppliers: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Delivered Orders Statistics API")
    print("=" * 60)
    
    # Test with sample supplier ID
    test_delivered_orders_stats()
    
    print("\n" + "=" * 60)
    print("🔍 Testing with real supplier ID from database")
    print("=" * 60)
    
    # Test with real supplier ID
    test_with_real_supplier_id() 
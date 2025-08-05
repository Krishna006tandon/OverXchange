import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_supplier_names():
    """Test to see what supplier names are in the orders"""
    try:
        # Get all orders
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if data['success']:
            print("✅ Orders retrieved successfully")
            print(f"Total orders: {len(data['orders'])}")
            
            # Check supplier names in each order
            for order in data['orders']:
                print(f"\n📦 Order ID: {order.get('order_id')}")
                if 'supplier_orders' in order:
                    for supplier_order in order['supplier_orders']:
                        print(f"   Supplier: '{supplier_order.get('supplier_name')}'")
                else:
                    print("   No supplier_orders found")
        else:
            print(f"❌ Failed to get orders: {data['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_supplier_names() 
import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_vendor_orders():
    """Test vendor orders with supplier status"""
    try:
        # First, let's see what orders are available
        print("📋 Getting all orders for debugging...")
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get orders: {data['message']}")
            return
        
        orders = data['orders']
        if not orders:
            print("❌ No orders found")
            return
        
        print(f"✅ Found {len(orders)} total orders")
        
        # Find orders with vendor_id
        vendor_orders = []
        for order in orders:
            if 'vendor_id' in order:
                vendor_orders.append(order)
        
        print(f"📦 Found {len(vendor_orders)} orders with vendor_id")
        
        # Show vendor orders with supplier status
        for order in vendor_orders:
            print(f"\n📋 Order: {order['order_id']}")
            print(f"   Vendor ID: {order.get('vendor_id')}")
            print(f"   Status: {order.get('status')}")
            print(f"   Date: {order.get('order_date')}")
            
            if 'supplier_orders' in order:
                print(f"   Supplier Orders ({len(order['supplier_orders'])}):")
                for supplier_order in order['supplier_orders']:
                    print(f"     - {supplier_order.get('supplier_name')}: {supplier_order.get('status')}")
                    if supplier_order.get('accepted_at'):
                        print(f"       Accepted: {supplier_order.get('accepted_at')}")
                    if supplier_order.get('estimated_delivery'):
                        print(f"       Est. Delivery: {supplier_order.get('estimated_delivery')}")
            else:
                print("   No supplier_orders found")
        
        # Test vendor-specific API call
        if vendor_orders:
            vendor_id = vendor_orders[0]['vendor_id']
            print(f"\n🔄 Testing vendor-specific API for vendor_id: {vendor_id}")
            
            response = requests.get(f"{BASE_URL}/api/orders?user_type=vendor&user_id={vendor_id}")
            vendor_data = response.json()
            
            if vendor_data['success']:
                print(f"✅ Vendor API successful - {len(vendor_data['orders'])} orders")
                for order in vendor_data['orders']:
                    print(f"   Order: {order['order_id']} - Status: {order.get('status')}")
                    if 'supplier_orders' in order:
                        for so in order['supplier_orders']:
                            print(f"     Supplier: {so.get('supplier_name')} - {so.get('status')}")
            else:
                print(f"❌ Vendor API failed: {vendor_data['message']}")
        else:
            print("❌ No vendor orders found to test")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_vendor_orders() 
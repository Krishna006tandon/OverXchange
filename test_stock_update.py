import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_stock_update():
    """Test stock update when order is accepted"""
    try:
        # First, let's see what orders are available
        print("📋 Getting available orders...")
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get orders: {data['message']}")
            return
        
        orders = data['orders']
        if not orders:
            print("❌ No orders found")
            return
        
        # Find a pending order
        pending_order = None
        for order in orders:
            if 'supplier_orders' in order:
                for supplier_order in order['supplier_orders']:
                    if supplier_order.get('status') == 'pending':
                        pending_order = order
                        supplier_name = supplier_order.get('supplier_name')
                        break
                if pending_order:
                    break
        
        if not pending_order:
            print("❌ No pending orders found")
            return
        
        print(f"✅ Found pending order: {pending_order['order_id']}")
        print(f"   Supplier: {supplier_name}")
        
        # Show items in the order
        for supplier_order in pending_order['supplier_orders']:
            if supplier_order.get('supplier_name') == supplier_name:
                print(f"   Items:")
                for item in supplier_order.get('items', []):
                    print(f"     - {item.get('name')}: {item.get('quantity')} units")
                break
        
        # Accept the order
        print(f"\n🔄 Accepting order {pending_order['order_id']}...")
        
        accept_data = {
            'supplier_name': supplier_name,
            'acceptance_notes': 'Test acceptance for stock update',
            'estimated_delivery': '2025-08-01'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orders/{pending_order['order_id']}/accept",
            json=accept_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Order accepted successfully!")
            print(f"   Message: {result['message']}")
            
            if result.get('stock_updated'):
                print(f"   📦 Stock Update: {result['stock_message']}")
                
                # Show updated items if available
                if 'updated_items' in result:
                    print("   Updated Items:")
                    for item in result['updated_items']:
                        print(f"     - {item['product']}: {item['previous_stock']} -> {item['new_stock']} (ordered: {item['ordered_quantity']})")
            else:
                print("   ⚠️ Stock update failed or not available")
        else:
            print(f"❌ Failed to accept order: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_stock_update() 
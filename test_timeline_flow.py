import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_timeline_flow():
    """Test order timeline flow"""
    try:
        print("📋 Testing Order Timeline Flow...")
        
        # Get all orders
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get orders: {data['message']}")
            return
        
        orders = data['orders']
        if not orders:
            print("❌ No orders found")
            return
        
        print(f"✅ Found {len(orders)} orders")
        
        # Test timeline flow for each order
        for order in orders:
            print(f"\n📦 Order: {order['order_id']}")
            print(f"   Main Status: {order.get('status')}")
            print(f"   Order Date: {order.get('order_date')}")
            
            if 'supplier_orders' in order:
                print(f"   Supplier Timeline:")
                for supplier_order in order['supplier_orders']:
                    supplier_name = supplier_order.get('supplier_name')
                    status = supplier_order.get('status')
                    
                    print(f"     - {supplier_name}: {status}")
                    
                    if status == 'accepted':
                        print(f"       Accepted: {supplier_order.get('accepted_at')}")
                        print(f"       Est. Delivery: {supplier_order.get('estimated_delivery')}")
                    elif status == 'processing':
                        print(f"       Processing: Items being prepared")
                    elif status == 'shipped':
                        print(f"       Shipped: Items dispatched")
                    elif status == 'delivered':
                        print(f"       Delivered: Successfully delivered")
                    elif status == 'rejected':
                        print(f"       Rejected: {supplier_order.get('rejection_reason')}")
            else:
                print("   No supplier_orders found")
            
            # Check if timeline flow is correct
            if 'supplier_orders' in order:
                all_accepted = all(so.get('status') == 'accepted' for so in order['supplier_orders'])
                any_processing = any(so.get('status') == 'processing' for so in order['supplier_orders'])
                any_shipped = any(so.get('status') == 'shipped' for so in order['supplier_orders'])
                any_delivered = any(so.get('status') == 'delivered' for so in order['supplier_orders'])
                any_rejected = any(so.get('status') == 'rejected' for so in order['supplier_orders'])
                
                print(f"   Timeline Check:")
                print(f"     All Accepted: {all_accepted}")
                print(f"     Any Processing: {any_processing}")
                print(f"     Any Shipped: {any_shipped}")
                print(f"     Any Delivered: {any_delivered}")
                print(f"     Any Rejected: {any_rejected}")
                
                # Validate flow
                if any_rejected:
                    print(f"     ⚠️  Order has rejected suppliers")
                elif all_accepted and not any_processing and not any_shipped and not any_delivered:
                    print(f"     ✅ Flow: Pending → Accepted")
                elif all_accepted and any_processing and not any_shipped and not any_delivered:
                    print(f"     ✅ Flow: Pending → Accepted → Processing")
                elif all_accepted and any_processing and any_shipped and not any_delivered:
                    print(f"     ✅ Flow: Pending → Accepted → Processing → Shipped")
                elif all_accepted and any_processing and any_shipped and any_delivered:
                    print(f"     ✅ Flow: Pending → Accepted → Processing → Shipped → Delivered")
                else:
                    print(f"     ⚠️  Mixed status flow")
        
        print(f"\n🎯 Timeline Flow Test Complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_timeline_flow() 
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

def check_orders():
    print("🔍 Checking orders in database...")
    print("=" * 50)
    
    # Get all orders
    orders = list(db['orders'].find())
    
    if not orders:
        print("❌ No orders found in database!")
        return
    
    print(f"✅ Found {len(orders)} orders in database:")
    print()
    
    for i, order in enumerate(orders, 1):
        print(f"📦 Order #{i}:")
        print(f"   MongoDB ID: {order['_id']}")
        
        # Check if it's our new order format
        if 'order_id' in order:
            print(f"   Order ID: {order['order_id']}")
            print(f"   Customer: {order['customer_info']['firstName']} {order['customer_info']['lastName']}")
            print(f"   Total Amount: ₹{order['total_amount']}")
            print(f"   Status: {order['status']}")
            print(f"   Vendor ID: {order.get('vendor_id', 'Not set')}")
            print(f"   Date: {order['order_date']}")
            print(f"   Items: {len(order['items'])} items")
            print(f"   Supplier Orders: {len(order['supplier_orders'])} suppliers")
            
            # Show supplier details
            for j, supplier_order in enumerate(order['supplier_orders'], 1):
                print(f"     Supplier #{j}: {supplier_order['supplier_name']} - ₹{supplier_order['subtotal']} - {supplier_order['status']}")
        else:
            # Show raw order data for debugging
            print(f"   Raw order data: {order}")
        
        print("-" * 50)
    
    # Check specific vendor orders
    print("\n🔍 Testing vendor orders API...")
    vendor_id = "test_vendor_123"
    vendor_orders = list(db['orders'].find({'vendor_id': vendor_id}))
    print(f"Orders for vendor {vendor_id}: {len(vendor_orders)}")
    
    # Check specific supplier orders
    print("\n🔍 Testing supplier orders API...")
    supplier_name = "Fresh Foods Ltd"
    supplier_orders = list(db['orders'].find({'supplier_orders.supplier_name': supplier_name}))
    print(f"Orders for supplier {supplier_name}: {len(supplier_orders)}")

if __name__ == "__main__":
    check_orders() 
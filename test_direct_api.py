#!/usr/bin/env python3
"""
Direct test of delivered orders functionality
"""

from pymongo import MongoClient
from bson import ObjectId

def test_delivered_orders_direct():
    """Test delivered orders functionality directly with MongoDB"""
    
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
    db = mongo_client['OverXchange']
    
    # Test supplier ID
    supplier_id = "688537c9b69abf0009982a2d"
    
    try:
        # Find supplier info
        supplier_info = db['suppliers'].find_one({'_id': ObjectId(supplier_id)})
        if not supplier_info:
            print("❌ Supplier not found")
            return
        
        supplier_name = supplier_info.get('business_name', supplier_info.get('name', ''))
        print(f"✅ Found supplier: {supplier_name}")
        
        # Get all orders for this supplier
        all_orders_query = {
            '$or': [
                {'supplier_orders.supplier_name': supplier_name},
                {'supplier_orders.supplier_id': supplier_id}
            ]
        }
        
        all_orders = list(db['orders'].find(all_orders_query))
        print(f"📦 Found {len(all_orders)} total orders")
        
        total_orders = 0
        delivered_orders = 0
        pending_orders = 0
        rejected_orders = 0
        total_delivered_value = 0
        
        for order in all_orders:
            print(f"\n📋 Order ID: {order.get('order_id', 'N/A')}")
            print(f"   Status: {order.get('status', 'N/A')}")
            
            for supplier_order in order.get('supplier_orders', []):
                if (supplier_order.get('supplier_name') == supplier_name or 
                    supplier_order.get('supplier_id') == supplier_id):
                    total_orders += 1
                    
                    status = supplier_order.get('status', 'pending')
                    print(f"   Supplier Order Status: {status}")
                    
                    if status == 'delivered':
                        delivered_orders += 1
                        # Calculate delivered order value
                        for item in supplier_order.get('items', []):
                            item_quantity = item.get('quantity', 0)
                            item_price = item.get('price', 0)
                            total_delivered_value += item_quantity * item_price
                    elif status == 'pending':
                        pending_orders += 1
                    elif status == 'rejected':
                        rejected_orders += 1
        
        # Calculate remaining orders (non-delivered)
        remaining_orders = total_orders - delivered_orders
        
        print("\n" + "=" * 60)
        print(f"📊 DELIVERED ORDERS STATISTICS FOR: {supplier_name}")
        print("=" * 60)
        print(f"📦 Total Orders: {total_orders}")
        print(f"✅ Delivered Orders: {delivered_orders}")
        print(f"⏳ Remaining Orders: {remaining_orders}")
        print(f"🔄 Pending Orders: {pending_orders}")
        print(f"❌ Rejected Orders: {rejected_orders}")
        print(f"💰 Total Delivered Value: ₹{total_delivered_value:.2f}")
        
        if total_orders > 0:
            delivery_rate = (delivered_orders / total_orders) * 100
            print(f"📈 Delivery Rate: {delivery_rate:.2f}%")
        else:
            print(f"📈 Delivery Rate: 0%")
        
        print("=" * 60)
        
        # Calculate and show the breakdown
        print("\n📋 ORDER BREAKDOWN:")
        print(f"   • Delivered: {delivered_orders} orders")
        print(f"   • Pending: {pending_orders} orders")
        print(f"   • Rejected: {rejected_orders} orders")
        print(f"   • Total: {total_orders} orders")
        
        print(f"\n🎯 REMAINING ORDERS TO DELIVER: {remaining_orders}")
        
        if total_orders > 0:
            completion_percentage = (delivered_orders / total_orders) * 100
            print(f"📊 COMPLETION: {completion_percentage:.1f}%")
        else:
            print("📊 COMPLETION: No orders yet")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing Delivered Orders Statistics Directly")
    print("=" * 60)
    test_delivered_orders_direct() 
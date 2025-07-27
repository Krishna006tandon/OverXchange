import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_stock_deduction():
    """Test stock deduction when order is accepted"""
    try:
        print("📋 Testing Stock Deduction...")
        
        # First, let's see what stocks are available
        print("\n1️⃣ Getting current stocks...")
        response = requests.get(f"{BASE_URL}/api/stocks")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get stocks: {data['message']}")
            return
        
        stocks = data['stocks']
        print(f"✅ Found {len(stocks)} stock items")
        
        # Show current stocks
        for stock in stocks:
            supplier_name = stock.get('supplier_name', 'Unknown')
            product_name = stock.get('product_name', stock.get('name', 'Unknown'))
            quantity = stock.get('quantity_available', stock.get('quantity', 0))
            print(f"   - {supplier_name}: {product_name} - {quantity} units")
        
        # Get orders to find a pending one
        print("\n2️⃣ Getting orders...")
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get orders: {data['message']}")
            return
        
        orders = data['orders']
        if not orders:
            print("❌ No orders found")
            return
        
        # Find a pending order with items that have stock
        pending_order = None
        supplier_name = None
        
        for order in orders:
            if 'supplier_orders' in order:
                for supplier_order in order['supplier_orders']:
                    if supplier_order.get('status') == 'pending':
                        # Check if this supplier has stock for the items
                        supplier_name = supplier_order.get('supplier_name')
                        items = supplier_order.get('items', [])
                        
                        # Check if supplier has stock for these items
                        # Try to find supplier by business_name in suppliers collection
                        supplier_stocks = []
                        for stock in stocks:
                            stock_product = stock.get('product_name', stock.get('name', ''))
                            stock_quantity = stock.get('quantity_available', stock.get('quantity', 0))
                            # For now, match by product name since supplier_name is not in stock data
                            if stock_product:
                                supplier_stocks.append(stock)
                        
                        if supplier_stocks and items:
                            # Check if at least one item has stock
                            for item in items:
                                item_name = item.get('name')
                                for stock in supplier_stocks:
                                    stock_product = stock.get('product_name', stock.get('name', ''))
                                    stock_quantity = stock.get('quantity_available', stock.get('quantity', 0))
                                    if stock_product == item_name and stock_quantity > 0:
                                        pending_order = order
                                        break
                                if pending_order:
                                    break
                        if pending_order:
                            break
                if pending_order:
                    break
        
        if not pending_order:
            print("❌ No pending orders with available stock found")
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
        
        # Show current stock for this supplier
        print(f"\n3️⃣ Current stock for {supplier_name}:")
        supplier_stocks = [s for s in stocks if s.get('supplier_name') == supplier_name]
        for stock in supplier_stocks:
            print(f"   - {stock.get('name')}: {stock.get('quantity')} units")
        
        # Accept the order
        print(f"\n4️⃣ Accepting order {pending_order['order_id']}...")
        
        accept_data = {
            'supplier_name': supplier_name,
            'acceptance_notes': 'Test acceptance for stock deduction',
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
            
            # Check updated stocks
            print(f"\n5️⃣ Checking updated stocks...")
            response = requests.get(f"{BASE_URL}/api/stocks")
            data = response.json()
            
            if data['success']:
                updated_stocks = data['stocks']
                supplier_updated_stocks = [s for s in updated_stocks if s.get('supplier_name') == supplier_name]
                
                print(f"   Updated stock for {supplier_name}:")
                for stock in supplier_updated_stocks:
                    print(f"     - {stock.get('name')}: {stock.get('quantity')} units")
            else:
                print(f"   ❌ Failed to get updated stocks: {data['message']}")
        else:
            print(f"❌ Failed to accept order: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_stock_deduction() 
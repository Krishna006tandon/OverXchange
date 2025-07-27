import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def debug_stock_update():
    """Debug stock update process"""
    try:
        print("🔍 Debugging Stock Update Process...")
        
        # Get stocks before update
        print("\n1️⃣ Getting stocks before update...")
        response = requests.get(f"{BASE_URL}/api/stocks")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get stocks: {data['message']}")
            return
        
        stocks_before = data['stocks']
        print(f"✅ Found {len(stocks_before)} stock items")
        
        # Show all stocks with details
        for i, stock in enumerate(stocks_before):
            print(f"\n📦 Stock {i+1}:")
            print(f"   ID: {stock.get('_id')}")
            print(f"   Product: {stock.get('product_name')}")
            print(f"   Quantity: {stock.get('quantity_available')}")
            print(f"   Supplier ID: {stock.get('supplier_id')}")
            print(f"   Raw data: {json.dumps(stock, indent=2)}")
        
        # Get suppliers to map supplier_id to name
        print(f"\n2️⃣ Getting suppliers...")
        response = requests.get(f"{BASE_URL}/api/suppliers")
        data = response.json()
        
        if data['success']:
            suppliers = data['suppliers']
            print(f"✅ Found {len(suppliers)} suppliers")
            
            # Create supplier mapping
            supplier_map = {}
            for supplier in suppliers:
                supplier_id = str(supplier.get('_id'))
                business_name = supplier.get('business_name', supplier.get('name', ''))
                supplier_map[supplier_id] = business_name
                print(f"   {supplier_id}: {business_name}")
        
        # Find a pending order with Motichur Laddo
        print(f"\n3️⃣ Finding pending order with Motichur Laddo...")
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if data['success']:
            orders = data['orders']
            
            # Find order with Motichur Laddo
            target_order = None
            target_supplier = None
            
            for order in orders:
                if 'supplier_orders' in order:
                    for supplier_order in order['supplier_orders']:
                        if supplier_order.get('status') == 'pending':
                            items = supplier_order.get('items', [])
                            for item in items:
                                if item.get('name') == 'Motichur Laddo':
                                    target_order = order
                                    target_supplier = supplier_order.get('supplier_name')
                                    break
                        if target_order:
                            break
                if target_order:
                    break
            
            if target_order:
                print(f"✅ Found order: {target_order['order_id']}")
                print(f"   Supplier: {target_supplier}")
                
                # Show items
                for supplier_order in target_order['supplier_orders']:
                    if supplier_order.get('supplier_name') == target_supplier:
                        for item in supplier_order.get('items', []):
                            print(f"   Item: {item.get('name')} - {item.get('quantity')} units")
                
                # Find corresponding stock
                print(f"\n4️⃣ Finding corresponding stock...")
                for stock in stocks_before:
                    if stock.get('product_name') == 'Motichur Laddo':
                        supplier_id = stock.get('supplier_id')
                        supplier_name = supplier_map.get(supplier_id, 'Unknown')
                        print(f"   Found stock:")
                        print(f"     Product: {stock.get('product_name')}")
                        print(f"     Quantity: {stock.get('quantity_available')}")
                        print(f"     Supplier ID: {supplier_id}")
                        print(f"     Supplier Name: {supplier_name}")
                        print(f"     Expected Supplier: {target_supplier}")
                        
                        # Check if supplier matches
                        if supplier_name == target_supplier:
                            print(f"     ✅ Supplier matches!")
                        else:
                            print(f"     ❌ Supplier mismatch!")
                
                # Accept the order
                print(f"\n5️⃣ Accepting order...")
                accept_data = {
                    'supplier_name': target_supplier,
                    'acceptance_notes': 'Debug test',
                    'estimated_delivery': '2025-08-01'
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/orders/{target_order['order_id']}/accept",
                    json=accept_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Check stocks after update
                print(f"\n6️⃣ Checking stocks after update...")
                response = requests.get(f"{BASE_URL}/api/stocks")
                data = response.json()
                
                if data['success']:
                    stocks_after = data['stocks']
                    
                    # Find the same stock
                    for stock in stocks_after:
                        if stock.get('product_name') == 'Motichur Laddo':
                            supplier_id = stock.get('supplier_id')
                            supplier_name = supplier_map.get(supplier_id, 'Unknown')
                            if supplier_name == target_supplier:
                                print(f"   Updated stock:")
                                print(f"     Product: {stock.get('product_name')}")
                                print(f"     Quantity: {stock.get('quantity_available')}")
                                print(f"     Supplier: {supplier_name}")
                                break
            else:
                print("❌ No pending order with Motichur Laddo found")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_stock_update() 
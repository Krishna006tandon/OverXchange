import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def debug_stocks():
    """Debug stock data structure"""
    try:
        print("🔍 Debugging Stock Data...")
        
        # Get stocks
        response = requests.get(f"{BASE_URL}/api/stocks")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get stocks: {data['message']}")
            return
        
        stocks = data['stocks']
        print(f"✅ Found {len(stocks)} stock items")
        
        # Show raw stock data
        for i, stock in enumerate(stocks):
            print(f"\n📦 Stock {i+1}:")
            print(f"   Raw data: {json.dumps(stock, indent=2)}")
            
            # Check for required fields
            supplier_name = stock.get('supplier_name')
            name = stock.get('name')
            quantity = stock.get('quantity')
            
            print(f"   supplier_name: {supplier_name}")
            print(f"   name: {name}")
            print(f"   quantity: {quantity}")
            
            if not supplier_name:
                print("   ⚠️  Missing supplier_name")
            if not name:
                print("   ⚠️  Missing name")
            if quantity is None:
                print("   ⚠️  Missing quantity")
        
        # Get orders to see what items are being ordered
        print(f"\n📋 Getting orders to see ordered items...")
        response = requests.get(f"{BASE_URL}/api/orders")
        data = response.json()
        
        if data['success']:
            orders = data['orders']
            print(f"✅ Found {len(orders)} orders")
            
            # Show items in orders
            for order in orders:
                print(f"\n📦 Order: {order.get('order_id')}")
                if 'supplier_orders' in order:
                    for supplier_order in order['supplier_orders']:
                        supplier_name = supplier_order.get('supplier_name')
                        print(f"   Supplier: {supplier_name}")
                        for item in supplier_order.get('items', []):
                            print(f"     - {item.get('name')}: {item.get('quantity')} units")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_stocks() 
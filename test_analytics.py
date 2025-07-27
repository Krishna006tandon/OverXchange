import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_analytics():
    """Test analytics with left stock value"""
    try:
        print("📊 Testing Analytics with Left Stock Value...")
        
        # Get suppliers to find a supplier ID
        print("\n1️⃣ Getting suppliers...")
        response = requests.get(f"{BASE_URL}/api/suppliers")
        data = response.json()
        
        if not data['success']:
            print(f"❌ Failed to get suppliers: {data['message']}")
            return
        
        suppliers = data['suppliers']
        if not suppliers:
            print("❌ No suppliers found")
            return
        
        # Use first supplier for testing
        supplier = suppliers[0]
        supplier_id = supplier['_id']
        supplier_name = supplier.get('business_name', supplier.get('name', 'Unknown'))
        
        print(f"✅ Testing with supplier: {supplier_name} (ID: {supplier_id})")
        
        # Test analytics API
        print(f"\n2️⃣ Testing analytics API...")
        response = requests.get(f"{BASE_URL}/api/dashboard/{supplier_id}")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analytics retrieved successfully!")
            
            analytics = data['analytics']
            print(f"\n   📊 Analytics Data:")
            print(f"     Total Products: {analytics['total_products']}")
            print(f"     Low Stock Items: {analytics['low_stock_items']}")
            print(f"     Out of Stock Items: {analytics['out_of_stock_items']}")
            print(f"     Total Value: ₹{analytics['total_value']:,.2f}")
            print(f"     Left Stock Value: ₹{analytics['left_stock_value']:,.2f}")
            
            # Check if values make sense
            if analytics['total_value'] >= 0:
                print(f"     ✅ Total Value is valid")
            else:
                print(f"     ❌ Total Value is negative!")
            
            if analytics['left_stock_value'] >= 0:
                print(f"     ✅ Left Stock Value is valid")
            else:
                print(f"     ❌ Left Stock Value is negative!")
            
            if analytics['total_value'] == analytics['left_stock_value']:
                print(f"     ✅ Total Value and Left Stock Value match (as expected)")
            else:
                print(f"     ⚠️  Total Value and Left Stock Value differ")
            
            # Show category distribution
            if 'category_distribution' in analytics:
                print(f"\n   📈 Category Distribution:")
                for category, count in analytics['category_distribution'].items():
                    print(f"     {category}: {count} products")
            
            # Show recent stocks
            if 'recent_stocks' in data:
                recent_stocks = data['recent_stocks']
                print(f"\n   📦 Recent Stocks ({len(recent_stocks)} items):")
                for stock in recent_stocks:
                    product_name = stock.get('product_name', 'Unknown')
                    quantity = stock.get('quantity_available', 0)
                    price = stock.get('price_per_unit', 0)
                    value = quantity * price
                    print(f"     {product_name}: {quantity} units @ ₹{price} = ₹{value:,.2f}")
            
        else:
            print(f"   ❌ Failed to get analytics: {response.text}")
        
        # Test with invalid supplier ID
        print(f"\n3️⃣ Testing with invalid supplier ID...")
        response = requests.get(f"{BASE_URL}/api/dashboard/invalid_id")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ✅ Correctly returned error for invalid ID")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
        
        print(f"\n🎯 Analytics Test Complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_analytics() 
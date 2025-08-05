from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

# Sample coupons data
sample_coupons = [
    {
        'code': 'WELCOME10',
        'title': 'Welcome Discount',
        'discount_type': 'percentage',
        'discount_value': 10,
        'min_order_amount': 500,
        'valid_from': datetime.now().isoformat(),
        'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
        'usage_limit': 100,
        'used_count': 0,
        'status': 'active',
        'supplier_id': 'supplier123',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'code': 'SAVE50',
        'title': 'Save ₹50',
        'discount_type': 'fixed',
        'discount_value': 50,
        'min_order_amount': 1000,
        'valid_from': datetime.now().isoformat(),
        'valid_until': (datetime.now() + timedelta(days=60)).isoformat(),
        'usage_limit': 50,
        'used_count': 0,
        'status': 'active',
        'supplier_id': 'supplier123',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'code': 'BULK20',
        'title': 'Bulk Order Discount',
        'discount_type': 'percentage',
        'discount_value': 20,
        'min_order_amount': 2000,
        'valid_from': datetime.now().isoformat(),
        'valid_until': (datetime.now() + timedelta(days=90)).isoformat(),
        'usage_limit': 25,
        'used_count': 0,
        'status': 'active',
        'supplier_id': 'supplier123',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'code': 'FIRST25',
        'title': 'First Order Special',
        'discount_type': 'percentage',
        'discount_value': 25,
        'min_order_amount': 300,
        'valid_from': datetime.now().isoformat(),
        'valid_until': (datetime.now() + timedelta(days=45)).isoformat(),
        'usage_limit': 200,
        'used_count': 0,
        'status': 'active',
        'supplier_id': 'supplier456',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'code': 'FLAT100',
        'title': 'Flat ₹100 Off',
        'discount_type': 'fixed',
        'discount_value': 100,
        'min_order_amount': 1500,
        'valid_from': datetime.now().isoformat(),
        'valid_until': (datetime.now() + timedelta(days=75)).isoformat(),
        'usage_limit': 75,
        'used_count': 0,
        'status': 'active',
        'supplier_id': 'supplier456',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
]

def add_sample_coupons():
    try:
        # Check if coupons already exist
        existing_count = db['coupons'].count_documents({})
        if existing_count > 0:
            print(f"Found {existing_count} existing coupons. Skipping sample data addition.")
            return
        
        # Insert sample coupons
        result = db['coupons'].insert_many(sample_coupons)
        print(f"Successfully added {len(result.inserted_ids)} sample coupons!")
        
        # Display added coupons
        print("\nAdded coupons:")
        for coupon in sample_coupons:
            print(f"- {coupon['title']} ({coupon['code']}) - {coupon['discount_value']}{'%' if coupon['discount_type'] == 'percentage' else '₹'} off for supplier {coupon['supplier_id']}")
            
    except Exception as e:
        print(f"Error adding sample coupons: {e}")

if __name__ == "__main__":
    add_sample_coupons() 
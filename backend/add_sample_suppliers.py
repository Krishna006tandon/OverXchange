from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os
from config import Config

# MongoDB setup with environment variable
mongo_client = MongoClient(Config.MONGODB_URI)
db = mongo_client[Config.DATABASE_NAME]

# Sample suppliers data
sample_suppliers = [
    {
        'name': 'Rajesh Kumar',
        'email': 'rajesh@freshfoods.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Fresh Foods Supplier',
        'phone': '+91 9876543210',
        'address': 'Mumbai, Maharashtra',
        'specialization': 'Fresh Vegetables and Fruits'
    },
    {
        'name': 'Priya Sharma',
        'email': 'priya@qualityingredients.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Quality Ingredients Co.',
        'phone': '+91 9876543211',
        'address': 'Delhi, NCR',
        'specialization': 'Premium Spices and Herbs'
    },
    {
        'name': 'Amit Patel',
        'email': 'amit@localmarket.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Local Market Supplier',
        'phone': '+91 9876543212',
        'address': 'Ahmedabad, Gujarat',
        'specialization': 'Local Produce and Dairy'
    },
    {
        'name': 'Sunita Verma',
        'email': 'sunita@organicfoods.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Organic Foods Ltd.',
        'phone': '+91 9876543213',
        'address': 'Pune, Maharashtra',
        'specialization': 'Organic Vegetables and Grains'
    },
    {
        'name': 'Vikram Singh',
        'email': 'vikram@premiumspices.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Premium Spices & Herbs',
        'phone': '+91 9876543214',
        'address': 'Jaipur, Rajasthan',
        'specialization': 'Premium Spices and Seasonings'
    },
    {
        'name': 'Meera Iyer',
        'email': 'meera@cityfresh.com',
        'password': generate_password_hash('password123'),
        'company_name': 'City Fresh Market',
        'phone': '+91 9876543215',
        'address': 'Bangalore, Karnataka',
        'specialization': 'Fresh Produce and Meat'
    },
    {
        'name': 'Arjun Reddy',
        'email': 'arjun@spiceparadise.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Spice Paradise',
        'phone': '+91 9876543216',
        'address': 'Hyderabad, Telangana',
        'specialization': 'Exotic Spices and Condiments'
    },
    {
        'name': 'Kavita Gupta',
        'email': 'kavita@vegekingdom.com',
        'password': generate_password_hash('password123'),
        'company_name': 'Vegetable Kingdom',
        'phone': '+91 9876543217',
        'address': 'Chennai, Tamil Nadu',
        'specialization': 'Fresh Vegetables and Greens'
    }
]

def add_sample_suppliers():
    try:
        # Check if suppliers already exist
        existing_count = db['suppliers'].count_documents({})
        if existing_count > 0:
            print(f"Found {existing_count} existing suppliers. Skipping sample data addition.")
            return
        
        # Insert sample suppliers
        result = db['suppliers'].insert_many(sample_suppliers)
        print(f"Successfully added {len(result.inserted_ids)} sample suppliers!")
        
        # Display added suppliers
        print("\nAdded suppliers:")
        for supplier in sample_suppliers:
            print(f"- {supplier['company_name']} ({supplier['email']})")
            
    except Exception as e:
        print(f"Error adding sample suppliers: {e}")

if __name__ == "__main__":
    add_sample_suppliers() 
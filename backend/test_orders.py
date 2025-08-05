from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

def create_sample_orders():
    # Sample order data
    sample_orders = [
        {
            'order_id': 'ORD-20241201-ABC123',
            'customer_info': {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '9876543210'
            },
            'shipping_address': {
                'addressLine1': '123 Main Street',
                'addressLine2': 'Apartment 4B',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'pincode': '400001',
                'country': 'India'
            },
            'shipping_method': 'standard',
            'delivery_instructions': 'Please deliver between 9 AM to 6 PM',
            'payment_method': 'cod',
            'items': [
                {
                    'id': 'item1',
                    'name': 'Fresh Tomatoes',
                    'price': 80.0,
                    'supplierName': 'Fresh Foods Ltd',
                    'category': 'Vegetables',
                    'unit': 'kg',
                    'quantity': 5,
                    'maxQuantity': 100
                },
                {
                    'id': 'item2',
                    'name': 'Onions',
                    'price': 40.0,
                    'supplierName': 'Fresh Foods Ltd',
                    'category': 'Vegetables',
                    'unit': 'kg',
                    'quantity': 3,
                    'maxQuantity': 50
                }
            ],
            'subtotal': 520.0,
            'shipping_cost': 50.0,
            'tax_amount': 93.6,
            'total_amount': 663.6,
            'order_date': datetime.now(),
            'status': 'pending',
            'vendor_id': 'test_vendor_123',
            'supplier_orders': [
                {
                    'supplier_name': 'Fresh Foods Ltd',
                    'supplier_id': 'test_supplier_456',
                    'items': [
                        {
                            'id': 'item1',
                            'name': 'Fresh Tomatoes',
                            'price': 80.0,
                            'supplierName': 'Fresh Foods Ltd',
                            'category': 'Vegetables',
                            'unit': 'kg',
                            'quantity': 5,
                            'maxQuantity': 100
                        },
                        {
                            'id': 'item2',
                            'name': 'Onions',
                            'price': 40.0,
                            'supplierName': 'Fresh Foods Ltd',
                            'category': 'Vegetables',
                            'unit': 'kg',
                            'quantity': 3,
                            'maxQuantity': 50
                        }
                    ],
                    'subtotal': 520.0,
                    'status': 'pending',
                    'order_date': datetime.now()
                }
            ]
        },
        {
            'order_id': 'ORD-20241201-DEF456',
            'customer_info': {
                'firstName': 'Jane',
                'lastName': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '9876543211'
            },
            'shipping_address': {
                'addressLine1': '456 Oak Avenue',
                'addressLine2': '',
                'city': 'Delhi',
                'state': 'Delhi',
                'pincode': '110001',
                'country': 'India'
            },
            'shipping_method': 'express',
            'delivery_instructions': 'Ring the bell twice',
            'payment_method': 'online',
            'items': [
                {
                    'id': 'item3',
                    'name': 'Basmati Rice',
                    'price': 120.0,
                    'supplierName': 'Grain Suppliers Co',
                    'category': 'Grains',
                    'unit': 'kg',
                    'quantity': 10,
                    'maxQuantity': 200
                }
            ],
            'subtotal': 1200.0,
            'shipping_cost': 150.0,
            'tax_amount': 216.0,
            'total_amount': 1566.0,
            'order_date': datetime.now(),
            'status': 'processing',
            'vendor_id': 'test_vendor_789',
            'supplier_orders': [
                {
                    'supplier_name': 'Grain Suppliers Co',
                    'supplier_id': 'test_supplier_789',
                    'items': [
                        {
                            'id': 'item3',
                            'name': 'Basmati Rice',
                            'price': 120.0,
                            'supplierName': 'Grain Suppliers Co',
                            'category': 'Grains',
                            'unit': 'kg',
                            'quantity': 10,
                            'maxQuantity': 200
                        }
                    ],
                    'subtotal': 1200.0,
                    'status': 'processing',
                    'order_date': datetime.now()
                }
            ]
        }
    ]
    
    # Insert sample orders
    for order in sample_orders:
        try:
            result = db['orders'].insert_one(order)
            print(f"Inserted order {order['order_id']} with ID: {result.inserted_id}")
        except Exception as e:
            print(f"Error inserting order {order['order_id']}: {e}")
    
    print("Sample orders created successfully!")

if __name__ == "__main__":
    create_sample_orders() 
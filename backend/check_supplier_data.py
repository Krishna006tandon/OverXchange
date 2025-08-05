from pymongo import MongoClient

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

def check_and_clean_supplier_data():
    try:
        # Get all suppliers
        suppliers = list(db['suppliers'].find({}))
        
        if not suppliers:
            print("No suppliers found in database.")
            return
        
        print("Current supplier data:")
        print("-" * 50)
        
        for supplier in suppliers:
            print(f"\nSupplier ID: {supplier['_id']}")
            print(f"Email: {supplier.get('email', 'N/A')}")
            print(f"Business Name: {supplier.get('business_name', 'N/A')}")
            print(f"Product Categories: {supplier.get('product_categories', 'N/A')}")
            print(f"Warehouse Address: {supplier.get('warehouse_address', 'N/A')}")
            print(f"GSTIN: {supplier.get('gstin', 'N/A')}")
            print(f"MOQ: {supplier.get('moq', 'N/A')}")
            
            # Check for fake/placeholder data
            fake_data_found = False
            fake_fields = []
            
            if supplier.get('product_categories') in ['wwee', 'test', 'demo', 'placeholder']:
                fake_data_found = True
                fake_fields.append('product_categories')
            
            if supplier.get('warehouse_address') in ['wwwee', 'test', 'demo', 'placeholder']:
                fake_data_found = True
                fake_fields.append('warehouse_address')
            
            if supplier.get('gstin') in ['wwee1234', 'test123', 'demo123', 'placeholder']:
                fake_data_found = True
                fake_fields.append('gstin')
            
            if supplier.get('moq') in ['10', 'test', 'demo']:
                fake_data_found = True
                fake_fields.append('moq')
            
            if fake_data_found:
                print(f"⚠️ FAKE DATA DETECTED in fields: {fake_fields}")
                
                # Ask if user wants to clean this data
                response = input(f"Remove fake data for supplier {supplier.get('email', 'N/A')}? (y/n): ")
                if response.lower() == 'y':
                    # Remove fake data
                    update_data = {}
                    if 'product_categories' in fake_fields:
                        update_data['product_categories'] = None
                    if 'warehouse_address' in fake_fields:
                        update_data['warehouse_address'] = None
                    if 'gstin' in fake_fields:
                        update_data['gstin'] = None
                    if 'moq' in fake_fields:
                        update_data['moq'] = None
                    
                    if update_data:
                        db['suppliers'].update_one(
                            {'_id': supplier['_id']},
                            {'$unset': update_data}
                        )
                        print("✅ Fake data removed!")
            else:
                print("✅ No fake data detected")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_clean_supplier_data() 
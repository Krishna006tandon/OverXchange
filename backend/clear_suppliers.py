from pymongo import MongoClient

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
db = mongo_client['OverXchange']

def clear_all_suppliers():
    try:
        # Count existing suppliers
        existing_count = db['suppliers'].count_documents({})
        print(f"Found {existing_count} existing suppliers in database.")
        
        if existing_count == 0:
            print("No suppliers found in database. Nothing to clear.")
            return
        
        # Clear all suppliers
        result = db['suppliers'].delete_many({})
        print(f"Successfully deleted {result.deleted_count} suppliers from database!")
        
        # Verify deletion
        remaining_count = db['suppliers'].count_documents({})
        print(f"Remaining suppliers in database: {remaining_count}")
        
        if remaining_count == 0:
            print("✅ All suppliers have been successfully cleared from the database.")
            print("Now only real suppliers will be shown in the dashboard.")
        else:
            print("⚠️ Some suppliers may still remain in the database.")
            
    except Exception as e:
        print(f"Error clearing suppliers: {e}")

if __name__ == "__main__":
    print("Clearing all suppliers from database...")
    clear_all_suppliers() 
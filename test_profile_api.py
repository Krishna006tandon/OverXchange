import requests
import json

# Test the deployed application
BASE_URL = "https://overxchange-production.up.railway.app"

def test_profile_api():
    """Test profile API functionality"""
    try:
        print("🔍 Testing Profile API...")
        
        # First, let's see what users are available
        print("\n1️⃣ Getting all users to find a vendor...")
        
        # Test with a known vendor ID from previous tests
        vendor_id = "6886364016517d3228bfa410"  # From previous test results
        
        print(f"   Testing with vendor ID: {vendor_id}")
        
        # Test GET profile
        print(f"\n2️⃣ Testing GET profile...")
        response = requests.get(f"{BASE_URL}/api/profile/vendor/{vendor_id}")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile retrieved successfully!")
            print(f"   Profile Data:")
            for key, value in data.items():
                if key not in ['password', '_id']:
                    print(f"     {key}: {value}")
        else:
            print(f"   ❌ Failed to get profile: {response.text}")
        
        # Test PUT profile (update)
        print(f"\n3️⃣ Testing PUT profile...")
        update_data = {
            'name': 'Test Vendor Updated',
            'email': 'testvendor@example.com'
        }
        
        response = requests.put(
            f"{BASE_URL}/api/profile/vendor/{vendor_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile updated successfully!")
            print(f"   Response: {data}")
        else:
            print(f"   ❌ Failed to update profile: {response.text}")
        
        # Test with invalid user ID
        print(f"\n4️⃣ Testing with invalid user ID...")
        response = requests.get(f"{BASE_URL}/api/profile/vendor/invalid_id")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"   ✅ Correctly returned 404 for invalid ID")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
        
        # Test with different user types
        print(f"\n5️⃣ Testing different user types...")
        
        # Test supplier profile
        supplier_id = "68863a7b16517d3228bfa414"  # Tun Tun Sweets from previous tests
        
        response = requests.get(f"{BASE_URL}/api/profile/supplier/{supplier_id}")
        
        print(f"   Supplier Profile Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Supplier profile retrieved!")
            print(f"   Business Name: {data.get('business_name', 'N/A')}")
        else:
            print(f"   ❌ Failed to get supplier profile: {response.text}")
        
        print(f"\n🎯 Profile API Test Complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_profile_api() 
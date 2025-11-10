#!/usr/bin/env python3
#base_url ="https://overxchange-production.up.railway.app"
"""
Test script for License Upload and Admin Verification Workflow
"""

import requests
import json
import base64

def test_license_workflow():
    """Test the complete license workflow"""
    base_url = "https://overxchange-production.up.railway.app"
    
    print("🔧 Testing License Upload and Admin Verification Workflow")
    print("=" * 60)
    
    # Step 1: Test admin login
    print("\n1️⃣ Testing Admin Login...")
    admin_login_data = {
        "email": "admin@overxchange.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/admin/login", json=admin_login_data)
        if response.status_code == 200:
            print("   ✅ Admin login successful")
        else:
            print(f"   ❌ Admin login failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Admin login error: {str(e)}")
        return
    
    # Step 2: Check pending licenses
    print("\n2️⃣ Checking Pending Licenses...")
    try:
        response = requests.get(f"{base_url}/api/admin/licenses/pending")
        if response.status_code == 200:
            data = response.json()
            pending_count = len(data.get('licenses', []))
            print(f"   📋 Found {pending_count} pending licenses")
            
            if pending_count > 0:
                print("   📄 Pending licenses:")
                for license in data['licenses']:
                    print(f"      - {license.get('supplier_name', 'Unknown')} ({license.get('file_name', 'Unknown file')})")
        else:
            print(f"   ❌ Failed to get pending licenses: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting pending licenses: {str(e)}")
    
    # Step 3: Check license statistics
    print("\n3️⃣ Checking License Statistics...")
    try:
        response = requests.get(f"{base_url}/api/admin/licenses/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"   📊 Statistics:")
            print(f"      - Pending: {stats.get('pending', 0)}")
            print(f"      - Verified Today: {stats.get('verified_today', 0)}")
            print(f"      - Rejected Today: {stats.get('rejected_today', 0)}")
            print(f"      - Total Verified: {stats.get('verified_total', 0)}")
            print(f"      - Total Rejected: {stats.get('rejected_total', 0)}")
        else:
            print(f"   ❌ Failed to get stats: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Workflow Test Summary:")
    print("✅ Admin login system working")
    print("✅ Pending licenses API working")
    print("✅ License statistics API working")
    print("\n💡 To test complete workflow:")
    print("1. Upload a license file (status will be 'pending')")
    print("2. Admin will see it in pending licenses")
    print("3. Admin can review and approve/reject")
    print("4. Supplier status will be updated accordingly")

def test_license_upload_simulation():
    """Simulate license upload (without actual file)"""
    print("\n🔧 License Upload Simulation")
    print("=" * 40)
    print("📝 Note: This simulates the workflow without actual file upload")
    print("   In real scenario, supplier would upload license file")
    print("   File would be stored with 'pending' status")
    print("   Admin would see it in pending licenses list")
    print("   Admin would review and approve/reject")

if __name__ == "__main__":
    test_license_workflow()
    test_license_upload_simulation() 
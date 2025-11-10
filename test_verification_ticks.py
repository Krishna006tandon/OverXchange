#!/usr/bin/env python3
"""
Full License Upload & Verification Workflow Test Script
Author: Kajal's Workflow Test
"""

import requests
import os

BASE_URL = "https://overxchange-production.up.railway.app"

# Dummy file create karenge agar exist nahi hai
DUMMY_FILE = "dummy_license.pdf"
if not os.path.exists(DUMMY_FILE):
    with open(DUMMY_FILE, "wb") as f:
        f.write(b"%PDF-1.4\n%Dummy PDF for testing\n")

def supplier_upload_license():
    """Supplier uploads license (dummy file)"""
    print("\n1️⃣ Supplier License Uploading...")
    files = {'license': open(DUMMY_FILE, 'rb')}
    data = {
        "supplier_id": "SAMPLE_SUPPLIER_ID",  # Replace with actual supplier id if available
        "notes": "Testing License Upload"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/supplier/license/upload", files=files, data=data)
        if response.status_code == 200:
            print("   ✅ License uploaded successfully (status = pending)")
            return True
        else:
            print(f"   ❌ License upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error during upload: {str(e)}")
        return False

def admin_login():
    """Admin login to perform actions"""
    print("\n2️⃣ Admin Login...")
    admin_login_data = {
        "email": "admin@overxchange.com",
        "password": "admin123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/admin/login", json=admin_login_data)
        if response.status_code == 200:
            print("   ✅ Admin login successful")
            return True
        else:
            print(f"   ❌ Admin login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error during admin login: {str(e)}")
        return False

def get_pending_licenses():
    """Get pending licenses for admin review"""
    print("\n3️⃣ Fetching Pending Licenses...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/licenses/pending")
        if response.status_code == 200:
            data = response.json()
            licenses = data.get('licenses', [])
            print(f"   📋 Pending licenses found: {len(licenses)}")
            for l in licenses:
                print(f"      - ID: {l.get('_id')} | Supplier: {l.get('supplier_name')} | File: {l.get('file_name')}")
            return licenses
        else:
            print(f"   ❌ Failed to fetch pending licenses: {response.text}")
            return []
    except Exception as e:
        print(f"   ❌ Error fetching pending licenses: {str(e)}")
        return []

def verify_license(license_id, action="approve"):
    """Approve or reject a license"""
    print(f"\n4️⃣ Performing Admin Action → {action.upper()} license {license_id}")
    approval_data = {
        "action": action,
        "notes": f"Test action: {action}",
        "license_number": "22119005000732",
        "business_name": "Test Business",
        "address": "Test Address"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/admin/license/verify/{license_id}", json=approval_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ License {action}d successfully!")
            else:
                print(f"   ❌ License {action} failed: {result.get('message')}")
        else:
            print(f"   ❌ License {action} request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error during license {action}: {str(e)}")

def check_stats():
    """Check updated license statistics"""
    print("\n5️⃣ Checking License Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/licenses/stats")
        if response.status_code == 200:
            stats = response.json().get('stats', {})
            print(f"   📊 Stats:")
            print(f"      - Pending: {stats.get('pending', 0)}")
            print(f"      - Verified Today: {stats.get('verified_today', 0)}")
            print(f"      - Rejected Today: {stats.get('rejected_today', 0)}")
            print(f"      - Total Verified: {stats.get('verified_total', 0)}")
            print(f"      - Total Rejected: {stats.get('rejected_total', 0)}")
        else:
            print(f"   ❌ Failed to get stats: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {str(e)}")

def run_full_workflow():
    print("🔧 Full License Workflow Test")
    print("="*60)
    
    if not supplier_upload_license():
        return
    
    if not admin_login():
        return
    
    pending = get_pending_licenses()
    if pending:
        first_license_id = pending[0].get('_id')
        action = input("\n👉 Approve or Reject this license? (approve/reject): ").strip().lower()
        if action not in ["approve", "reject"]:
            print("   ❌ Invalid action. Defaulting to approve.")
            action = "approve"
        verify_license(first_license_id, action)
    else:
        print("   ℹ️  No pending licenses to review.")
    
    check_stats()

if __name__ == "__main__":
    run_full_workflow()

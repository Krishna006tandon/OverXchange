#!/usr/bin/env python3
"""
Test script for Super Admin login
"""

import requests
import json

def test_super_admin_login():
    """Test super admin login"""
    url = "https://overxchange-production.up.railway.app/api/admin/login"
    
    # Super admin credentials
    super_admin_data = {
        "email": "admin@overxchange.com",
        "password": "admin123"
    }
    
    try:
        print("🔧 Testing Super Admin Login")
        print("=" * 40)
        print(f"Email: {super_admin_data['email']}")
        print(f"Password: {super_admin_data['password']}")
        print()
        
        response = requests.post(url, json=super_admin_data, timeout=10)
        
        print(f"✅ POST {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login Successful!")
            print(f"   Admin ID: {result.get('admin_id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Role: {result.get('role')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Login Time: {result.get('login_time')}")
            
            if result.get('role') == 'super_admin':
                print("   🎯 This is a SUPER ADMIN account!")
            else:
                print("   ⚠️  This is a regular admin account")
                
        else:
            print(f"   ❌ Login Failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_regular_admin_login():
    """Test regular admin login for comparison"""
    url = "https://overxchange-production.up.railway.app/api/admin/login"
    
    # Regular admin credentials
    admin_data = {
        "email": "admin@gmail.com",
        "password": "admin"
    }
    
    try:
        print("\n🔧 Testing Regular Admin Login")
        print("=" * 40)
        print(f"Email: {admin_data['email']}")
        print(f"Password: {admin_data['password']}")
        print()
        
        response = requests.post(url, json=admin_data, timeout=10)
        
        print(f"✅ POST {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login Successful!")
            print(f"   Admin ID: {result.get('admin_id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Role: {result.get('role')}")
            print(f"   Email: {result.get('email')}")
            
            if result.get('role') == 'super_admin':
                print("   🎯 This is a SUPER ADMIN account!")
            else:
                print("   📋 This is a regular admin account")
                
        else:
            print(f"   ❌ Login Failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🎯 Super Admin Login Tester")
    print("=" * 50)
    
    # Test super admin login
    test_super_admin_login()
    
    # Test regular admin login for comparison
    test_regular_admin_login()
    
    print("\n" + "=" * 50)
    print("📋 Available Admin Accounts:")
    print("1. Super Admin: admin@overxchange.com / admin123")
    print("2. Regular Admin: admin@gmail.com / admin")
    print("\n💡 Super Admin has higher privileges!")

if __name__ == "__main__":
    main() 
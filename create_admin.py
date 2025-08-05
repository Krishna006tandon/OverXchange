#!/usr/bin/env python3
"""
Simple script to create admin accounts in the database
Usage: python create_admin.py
"""

import requests
import json

def create_admin(email, password, name="Admin User", role="admin"):
    """Create admin account using API"""
    url = "http://localhost:5000/api/admin/create"
    
    data = {
        "email": email,
        "password": password,
        "name": name,
        "role": role
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Admin created successfully!")
            print(f"   Email: {result.get('email')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Role: {result.get('role')}")
        else:
            print(f"❌ Failed to create admin: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🔧 Admin Account Creator")
    print("=" * 30)
    
    # Create admin@gmail.com account
    print("\n📧 Creating admin@gmail.com account...")
    create_admin(
        email="admin@gmail.com",
        password="admin",
        name="Admin User",
        role="admin"
    )
    
    print("\n" + "=" * 30)
    print("🎯 Available Admin Accounts:")
    print("1. admin@overxchange.com / admin123 (Super Admin)")
    print("2. admin@gmail.com / admin (Admin)")
    print("\n💡 You can now login with either account!")

if __name__ == "__main__":
    main() 
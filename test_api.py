#!/usr/bin/env python3
"""
Test script to check if the API endpoints are working
"""

import requests
import json

def test_api_endpoint(url, method='GET', data=None):
    """Test an API endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        print(f"✅ {method} {url}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
        print()
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {url}")
        print(f"   Error: Could not connect to server")
        print()
        return False
    except Exception as e:
        print(f"❌ {method} {url}")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    print("🔧 API Endpoint Tester")
    print("=" * 50)
    
    # Test base URL
    base_url = "https://overxchange-production.up.railway.app"
    
    # Test basic endpoints
    print("Testing basic endpoints...")
    test_api_endpoint(f"{base_url}/")
    test_api_endpoint(f"{base_url}/api/login", method='POST', data={
        "username": "test@test.com",
        "password": "test123"
    })
    
    # Test admin endpoints
    print("Testing admin endpoints...")
    test_api_endpoint(f"{base_url}/api/admin/login", method='POST', data={
        "email": "admin@gmail.com",
        "password": "admin"
    })
    
    # Test admin license endpoints
    print("Testing admin license endpoints...")
    test_api_endpoint(f"{base_url}/api/admin/licenses/pending")
    test_api_endpoint(f"{base_url}/api/admin/licenses/stats")
    
    print("=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
OverXchange Setup Test Script
This script tests all components to ensure everything is working correctly.
"""

import os
import sys
import subprocess
import requests
import time

def test_python_packages():
    """Test if all required Python packages are installed"""
    print("🔍 Testing Python packages...")
    
    required_packages = [
        'flask', 'flask_cors', 'pymongo', 'werkzeug', 
        'requests', 'bs4', 'lxml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        return False
    
    print("✅ All Python packages are installed")
    return True

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        
        # Use the same connection string as in app.py
        client = MongoClient('mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/')
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Test database access
        db = client['OverXchange']
        collections = db.list_collection_names()
        print(f"✅ Database 'OverXchange' accessible")
        print(f"   Collections found: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'frontend/index.html',
        'frontend/login.html',
        'frontend/signup.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files exist")
    return True

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🔍 Testing Flask application...")
    
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        original_dir = os.getcwd()
        os.chdir(backend_dir)
        
        # Add backend directory to Python path
        sys.path.insert(0, backend_dir)
        
        # Import the app
        from app import app
        
        print("✅ Flask app imported successfully")
        
        # Test basic routes
        with app.test_client() as client:
            # Test root route
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Root route working")
            else:
                print(f"❌ Root route failed: {response.status_code}")
                return False
            
            # Test API health check
            response = client.get('/api/suppliers')
            if response.status_code in [200, 404]:  # 404 is okay if no suppliers
                print("✅ API routes accessible")
            else:
                print(f"❌ API routes failed: {response.status_code}")
                return False
        
        # Restore original directory
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        # Restore original directory even if test fails
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

def main():
    print("🚀 OverXchange Setup Test")
    print("=" * 50)
    
    # Test all components
    tests = [
        test_python_packages,
        test_file_structure,
        test_mongodb_connection,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your OverXchange application is ready to run!")
        print("\nTo start the application:")
        print("  Windows: Double-click 'run_app.bat'")
        print("  Or run: python run_app.py")
        print("\nThe application will be available at: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing Python packages: pip install -r backend/requirements.txt")
        print("2. Check MongoDB connection")
        print("3. Ensure all files are in the correct locations")

if __name__ == "__main__":
    main() 
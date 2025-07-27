#!/usr/bin/env python3
"""
OverXchange Application Launcher
This script launches the Flask application from the correct directory.
"""

import os
import sys
import subprocess

def main():
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    if not os.path.exists(backend_dir):
        print("Error: Backend directory not found!")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if requirements are installed
    try:
        import flask
        import flask_cors
        import pymongo
        import werkzeug
        import requests
        import bs4
        import lxml
        print("✓ All required packages are installed")
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    
    # Run the Flask app
    print("🚀 Starting OverXchange application...")
    print("📱 Frontend will be available at: http://localhost:5000")
    print("🔧 API endpoints will be available at: http://localhost:5000/api/")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    main() 
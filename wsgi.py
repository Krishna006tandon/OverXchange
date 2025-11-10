#!/usr/bin/env python3
"""
WSGI entry point for Railway deployment
"""

import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Import the Flask app
from app import app
print("Flask app imported successfully from backend/app.py")

if __name__ == "__main__":
    # Get port from environment variable for Railway deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 
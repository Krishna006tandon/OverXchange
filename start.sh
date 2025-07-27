#!/bin/bash
echo "Starting OverXchange application..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting Flask application..."
python backend/app.py 
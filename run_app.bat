@echo off
echo ========================================
echo    OverXchange Application Launcher
echo ========================================
echo.

cd backend

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Installing/updating requirements...
pip install -r requirements.txt

echo.
echo Starting OverXchange application...
echo Frontend: http://localhost:5000
echo API: http://localhost:5000/api/
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python app.py

pause 
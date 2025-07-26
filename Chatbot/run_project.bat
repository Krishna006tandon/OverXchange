@echo off
echo ============================================
echo   Starting Street Food Chatbot Project
echo ============================================

:: --- Start Flask Backend ---
cd backend
echo Starting Flask backend...
start cmd /k "python app.py"

:: --- Start React Frontend ---
cd ../frontend
echo Starting React frontend..
start cmd /k "npm start"

echo Project started successfully!
echo Open http://localhost:3000 in your browser.
pause

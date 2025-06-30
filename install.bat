@echo off
echo 🏌️ Golf Database - Quick Install
echo ==============================

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python packages...
pip install -r requirements.txt

echo 🎯 Installation complete!
echo.
echo Next steps:
echo 1. Copy .env.template to .env and configure
echo 2. Run: python src\api\app.py
echo 3. Visit: http://localhost:5000

pause

@echo off
echo =========================================
echo BES Management System - Windows Launcher
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed! Please install Python from python.org
    pause
    exit /b
)

REM Create virtual environment if it doesn't exist
if not exist "venv_windows" (
    echo 🔨 Creating virtual environment...
    python -m venv venv_windows
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv_windows\Scripts\activate.bat

REM Install requirements
echo 📦 Checking/Installing requirements...
pip install -r requirements.txt

echo.
echo 🧪 Testing database connection...
python test_db_connection.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Database connection failed!
    echo Please make sure Laragon is running and MySQL is started.
    pause
    exit /b
)

echo.
echo 🚀 Starting Application...
python gui/run_app.py

pause

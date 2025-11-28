@echo off
echo ==========================================
echo DeepFake Detection System - Auto Setup
echo ==========================================

echo.
echo [1/4] Installing Backend Dependencies...
cd server
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python dependencies. Please check Python installation.
    pause
    exit /b
)

echo.
echo [2/4] Installing Frontend Dependencies...
cd ../client
call npm install
if %errorlevel% neq 0 (
    echo Failed to install Node dependencies. Please check Node.js installation.
    pause
    exit /b
)

echo.
echo [3/4] Setup Complete!
echo.
echo To run the system:
echo 1. Open Terminal 1: cd server ^& uvicorn main:app --reload
echo 2. Open Terminal 2: cd client ^& npm run dev
echo.
pause

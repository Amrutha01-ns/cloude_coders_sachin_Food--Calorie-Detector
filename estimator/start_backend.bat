@echo off
echo ============================================================
echo Starting Food Analysis Backend Server
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask not found. Installing dependencies...
    pip install flask flask-cors openai
)

echo.
echo Starting backend server on http://localhost:4000
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python backend.py

pause


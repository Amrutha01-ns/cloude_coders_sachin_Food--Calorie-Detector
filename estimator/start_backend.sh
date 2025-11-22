#!/bin/bash

echo "============================================================"
echo "Starting Food Analysis Backend Server"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python found!"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Flask not found. Installing dependencies..."
    pip3 install flask flask-cors openai
fi

echo ""
echo "Starting backend server on http://localhost:4000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "============================================================"
echo ""

python3 backend.py


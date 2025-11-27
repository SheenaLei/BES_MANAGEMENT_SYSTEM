#!/bin/bash
# Installation script for BES Management System

echo "========================================="
echo "BES Management System - Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi
echo "✅ Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages!"
    exit 1
fi
echo "✅ All packages installed successfully"
echo ""

# Check MySQL
echo "Checking MySQL..."
mysql --version 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  MySQL client not found. Please install MySQL Server."
    echo "   Ubuntu/WSL: sudo apt install mysql-server"
else
    echo "✅ MySQL found"
fi
echo ""

echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Set up MySQL database (see SETUP_GUIDE.md)"
echo "2. Run: python3 scripts/seed_admin.py"
echo "3. Run: python3 gui/run_app.py"
echo ""
echo "To activate virtual environment later:"
echo "  source venv/bin/activate"
echo ""

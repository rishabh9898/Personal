#!/bin/bash

# HR Recruitment Agent System - Setup Script
# This script automates the installation process

set -e  # Exit on error

echo "========================================"
echo "HR Recruitment Agent System Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ All dependencies installed"
echo ""

# Setup environment file
echo "Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠ .env file already exists. Skipping creation."
else
    cp .env.example .env
    echo "✓ Created .env file from template"
fi
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p backend/data/resumes
mkdir -p backend/data/results
echo "✓ Data directories created"
echo ""

# Final instructions
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit the .env file and add your OpenAI API key:"
echo "   nano .env  # or use your preferred editor"
echo ""
echo "2. Get your OpenAI API key from:"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "3. Run the application:"
echo "   python run.py"
echo ""
echo "4. Open your browser to:"
echo "   http://localhost:8000"
echo ""
echo "For more information, see:"
echo "  - README.md for full documentation"
echo "  - QUICK_START.md for a quick guide"
echo ""
echo "Happy recruiting! 🚀"
echo ""

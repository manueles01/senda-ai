#!/bin/bash

# Senda AI Setup Script
# This script helps you set up the development environment

set -e

echo "🚀 Setting up Senda AI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your configuration."
    echo "You can copy .env.example.txt as a starting point."
else
    echo "✅ .env file found"
fi

# Check for Google Cloud credentials
echo ""
if [ ! -f "service-account-key.json" ]; then
    echo "⚠️  Google Cloud service account key not found!"
    echo "Please download your service account key from Google Cloud Console"
    echo "and save it as service-account-key.json"
else
    echo "✅ Google Cloud credentials found"
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure your .env file with API keys and credentials"
echo "3. Set up Google Cloud service account credentials"
echo "4. Run the API server: uvicorn apps.api.app.main:app --reload"
echo ""
echo "For more information, see README.md"

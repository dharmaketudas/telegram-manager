#!/bin/bash

# Telegram Contact Manager Backend - Startup Script
# This script sets up and runs the FastAPI backend server

set -e  # Exit on error

echo "🚀 Starting Telegram Contact Manager Backend..."

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Must be run from the backend directory"
    echo "   Run: cd telegram-manager/backend && ./run.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your Telegram API credentials:"
    echo "   - API_ID (get from https://my.telegram.org/apps)"
    echo "   - API_HASH (get from https://my.telegram.org/apps)"
    echo "   - PHONE (your phone number in international format)"
    echo ""
    echo "Press Enter to edit .env now, or Ctrl+C to exit and edit manually"
    read -r
    ${EDITOR:-nano} .env
fi

# Create data directories
echo "📁 Ensuring data directories exist..."
mkdir -p data/media/profile-photos
mkdir -p data/media/group-photos
mkdir -p data/sessions

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo ""
echo "✨ Starting FastAPI server..."
echo "   API: http://localhost:${API_PORT:-8000}"
echo "   Docs: http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python start.py

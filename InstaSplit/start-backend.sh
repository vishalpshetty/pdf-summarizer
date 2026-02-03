#!/bin/bash
# Quick start script for backend (native Python)

cd "$(dirname "$0")/backend"

echo "🔙 Starting InstaSplit Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencies installed!"
fi

# Load environment variables
echo "🔐 Loading environment variables..."
export $(cat ../.env | grep -v '^#' | xargs)

# Start the server
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

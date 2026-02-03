#!/bin/bash
# Quick start script for frontend (native Python)

cd "$(dirname "$0")/frontend"

echo "🎨 Starting InstaSplit Frontend..."
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
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencies installed!"
fi

# Load environment variables
echo "🔐 Loading environment variables..."
export BACKEND_URL=$(grep BACKEND_URL ../.env | cut -d '=' -f2)

# Start Streamlit
echo ""
echo "🚀 Starting Streamlit frontend on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py

#!/bin/bash

# PDF Summarizer Setup Script
# This script helps you set up the project for local development

echo "🚀 PDF Summarizer - Setup Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 detected: $(python3 --version)"
echo ""

# Create virtual environment (optional but recommended)
read -p "📦 Do you want to create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "   To activate it later, run: source venv/bin/activate"
    echo ""
fi

# Setup Backend
echo "🔧 Setting up Backend..."
cd backend

# Create .env file
if [ ! -f .env ]; then
    echo "Creating backend/.env file..."
    cp .env.example .env
    echo "✅ Created backend/.env"
    echo "⚠️  Please edit backend/.env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - LANGSMITH_API_KEY (optional)"
    echo ""
else
    echo "✅ backend/.env already exists"
fi

# Install backend dependencies
echo "Installing backend dependencies..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Create .env file
if [ ! -f .env ]; then
    echo "Creating frontend/.env file..."
    cp .env.example .env
    echo "✅ Created frontend/.env"
else
    echo "✅ frontend/.env already exists"
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

cd ..

# Final instructions
echo ""
echo "🎉 Setup Complete!"
echo "=================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit your API keys in backend/.env:"
echo "   nano backend/.env"
echo ""
echo "2. Start the backend server (in a terminal):"
echo "   cd backend"
echo "   python3 -m uvicorn main:app --reload --port 8000"
echo ""
echo "3. Start the frontend (in a NEW terminal):"
echo "   cd frontend"
echo "   python3 -m streamlit run app.py"
echo ""
echo "4. Open your browser to: http://localhost:8501"
echo ""
echo "📚 For detailed instructions, see:"
echo "   - QUICKSTART.md (for local development)"
echo "   - DEPLOYMENT.md (for Railway deployment)"
echo "   - README.md (for overview)"
echo ""
echo "Happy coding! 🚀"

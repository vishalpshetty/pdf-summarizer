#!/bin/bash

# InstaSplit Setup Script
# Automated setup for local development

set -e  # Exit on error

echo "🧾 InstaSplit Setup Script"
echo "=========================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker not found (optional)"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "Choose setup method:"
echo "1) Docker Compose (recommended)"
echo "2) Native Python"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    if [ "$DOCKER_AVAILABLE" == false ]; then
        echo "❌ Docker is not available. Please install Docker or choose option 2."
        exit 1
    fi
    
    echo ""
    echo "📦 Setting up with Docker Compose..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        echo "Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys!"
        echo ""
        read -p "Press Enter after you've updated .env with your keys..."
    fi
    
    echo "Building Docker containers..."
    docker-compose build
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the application:"
    echo "  docker-compose up"
    echo ""
    echo "Then visit:"
    echo "  Frontend: http://localhost:8501"
    echo "  Backend:  http://localhost:8000"
    echo ""

elif [ "$choice" == "2" ]; then
    echo ""
    echo "🐍 Setting up with Native Python..."
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing frontend dependencies..."
    pip install -r requirements.txt
    
    cd ..
    
    # Environment variables
    if [ ! -f .env ]; then
        echo ""
        echo "Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys!"
    fi
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the backend:"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  export $(cat ../.env | xargs)"
    echo "  uvicorn app.main:app --reload"
    echo ""
    echo "To start the frontend (in another terminal):"
    echo "  cd frontend"
    echo "  source venv/bin/activate"
    echo "  export BACKEND_URL=http://localhost:8000"
    echo "  streamlit run streamlit_app.py"
    echo ""
    
else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo "📚 Documentation:"
echo "  README.md       - General overview"
echo "  DEVELOPMENT.md  - Development guide"
echo "  DEPLOYMENT.md   - Deployment guide"
echo ""
echo "Happy bill splitting! 🎉"

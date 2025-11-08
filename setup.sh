#!/bin/bash

# VendorLens Setup Script
# This script helps set up the development environment

echo "🚀 Setting up VendorLens..."

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your MongoDB URI and Nemotron API key"
else
    echo "✓ .env file already exists"
fi

# Backend setup
echo ""
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo ""
echo "⚛️  Setting up Next.js frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "✓ Node modules already installed"
fi

cd ..

# Create uploads directory
echo ""
echo "📁 Creating uploads directory..."
mkdir -p backend/uploads

# Start MongoDB with Docker Compose
echo ""
echo "🗄️  Starting MongoDB with Docker Compose..."
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your MongoDB URI and Nemotron API key"
echo "2. Start backend: cd backend && source venv/bin/activate && python main.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo ""
echo "Backend will run on http://localhost:8000"
echo "Frontend will run on http://localhost:3000"


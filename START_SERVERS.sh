#!/bin/bash

# VendorLens - Start Both Servers Script
# This script starts both backend and frontend servers for local development

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       VendorLens - Starting Backend & Frontend Servers      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists in backend
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: backend/.env file not found!${NC}"
    echo "Please create backend/.env with MongoDB and Nemotron credentials"
    exit 1
fi

# Check if .env.local exists in frontend
if [ ! -f "$SCRIPT_DIR/frontend/.env.local" ]; then
    echo -e "${YELLOW}Creating frontend/.env.local...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > "$SCRIPT_DIR/frontend/.env.local"
fi

echo -e "${BLUE}[1/2] Starting Backend Server...${NC}"
echo "------------------------------------------------------"
cd "$SCRIPT_DIR/backend"
python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend PID: $BACKEND_PID${NC}"
echo -e "${GREEN}✓ Backend URL: http://localhost:8000${NC}"
echo -e "${GREEN}✓ API Docs: http://localhost:8000/docs${NC}"
echo ""

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may not be ready yet...${NC}"
fi

echo ""
echo -e "${BLUE}[2/2] Starting Frontend Server...${NC}"
echo "------------------------------------------------------"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend PID: $FRONTEND_PID${NC}"
echo -e "${GREEN}✓ Frontend URL: http://localhost:3000${NC}"
echo ""

# Wait for frontend to start
sleep 8

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     ✅ SERVERS RUNNING!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to press Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait


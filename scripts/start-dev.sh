#!/bin/bash

# Development Server Startup Script
# This script starts the development servers for both frontend and backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down development servers..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_success "Development servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "========================================"
echo "  Starting Development Servers"
echo "========================================"

# Check if services are running
print_status "Checking if database services are running..."
if ! docker ps | grep -q "coding_platform_mysql"; then
    print_status "Starting database services..."
    cd docker
    docker-compose up -d mysql redis
    cd ..
    sleep 5
    print_success "Database services started"
else
    print_success "Database services are already running"
fi

# Start backend server
print_status "Starting backend server..."
cd backend

if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..

print_success "Backend server started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 3

# Start frontend server
print_status "Starting frontend server..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_error "Node modules not found. Please run setup.sh first."
    exit 1
fi

npm start &
FRONTEND_PID=$!
cd ..

print_success "Frontend server started (PID: $FRONTEND_PID)"

echo "========================================"
print_success "Development servers are running!"
echo "========================================"
echo ""
echo "Services:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:5000"
echo "  🗄️  MySQL: localhost:3306"
echo "  🚀 Redis: localhost:6379"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
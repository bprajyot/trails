#!/bin/bash

# Coding Challenge Platform Setup Script
# This script sets up the development environment for the coding challenge platform

set -e

echo "🚀 Setting up Coding Challenge Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'.' -f1 | cut -d'v' -f2)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18 or higher is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) is installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_VERSION" -lt 9 ]; then
        print_error "Python 3.9 or higher is required. Current version: $(python3 --version)"
        exit 1
    fi
    
    print_success "Python $(python3 --version) is installed"
}

# Create environment files
create_env_files() {
    print_status "Creating environment files..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        print_success "Created backend/.env from template"
        print_warning "Please update backend/.env with your actual configuration"
    else
        print_warning "backend/.env already exists, skipping..."
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:5000
REACT_APP_FIREBASE_API_KEY=your_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
EOF
        print_success "Created frontend/.env from template"
        print_warning "Please update frontend/.env with your actual Firebase configuration"
    else
        print_warning "frontend/.env already exists, skipping..."
    fi
}

# Install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created Python virtual environment"
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
    print_success "Backend dependencies installed"
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    cd frontend
    
    if [ ! -f "package-lock.json" ]; then
        npm install
    else
        npm ci
    fi
    
    cd ..
    print_success "Frontend dependencies installed"
}

# Build Docker images
build_docker_images() {
    print_status "Building Docker images..."
    
    # Build code execution images
    docker build -t coding-platform-python docker/executor/python/
    print_success "Built Python executor image"
    
    # You can add more language images here
    # docker build -t coding-platform-javascript docker/executor/javascript/
    # docker build -t coding-platform-java docker/executor/java/
    
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_status "Starting services with Docker Compose..."
    cd docker
    docker-compose up -d mysql redis
    
    # Wait for MySQL to be ready
    print_status "Waiting for MySQL to be ready..."
    sleep 10
    
    cd ..
    print_success "Database services started"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Wait a bit more for MySQL to be fully ready
    sleep 5
    
    # Run database initialization
    cd backend
    source venv/bin/activate
    
    # Create tables
    python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
    
    # Seed initial data
    python -c "from app import create_app; app = create_app(); app.app_context().push(); app.cli.commands['seed-db'].callback()"
    
    cd ..
    print_success "Database initialized with sample data"
}

# Main setup process
main() {
    echo "========================================"
    echo "  Coding Challenge Platform Setup"
    echo "========================================"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_docker
    check_node
    check_python
    
    # Setup process
    create_env_files
    install_backend_deps
    install_frontend_deps
    build_docker_images
    start_services
    init_database
    
    echo "========================================"
    print_success "Setup completed successfully!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Update environment files with your configuration:"
    echo "   - backend/.env"
    echo "   - frontend/.env"
    echo ""
    echo "2. Start the development servers:"
    echo "   - Backend: cd backend && source venv/bin/activate && python run.py"
    echo "   - Frontend: cd frontend && npm start"
    echo ""
    echo "3. Or use the start script: ./scripts/start-dev.sh"
    echo ""
    echo "4. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:5000"
    echo ""
    echo "Default admin credentials:"
    echo "   - Username: admin"
    echo "   - Password: admin123"
    echo ""
}

# Run main function
main "$@"
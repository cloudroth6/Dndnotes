#!/bin/bash

# D&D Note-Taking Application - Local Setup Script
# This script sets up the application for local development

set -e

echo "🎲 Setting up D&D Note-Taking Application..."

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
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
else
    print_warning ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p data/mongodb
mkdir -p logs

print_success "Directories created"

# Check if ports are available
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use (needed for $service)"
        print_warning "Consider changing the port in .env file"
        return 1
    else
        print_success "Port $port is available for $service"
        return 0
    fi
}

print_status "Checking port availability..."

# Source .env file to get port configurations
source .env 2>/dev/null || true

# Check default ports
check_port ${FRONTEND_PORT:-3000} "Frontend"
check_port ${BACKEND_PORT:-8001} "Backend" 
check_port ${MONGO_PORT:-27017} "MongoDB"

# Build and start services
print_status "Building Docker images..."
docker-compose build

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    print_success "MongoDB is healthy"
else
    print_error "MongoDB is not responding"
fi

# Check Backend
backend_port=${BACKEND_PORT:-8001}
if curl -s http://localhost:$backend_port/api/ >/dev/null 2>&1; then
    print_success "Backend API is healthy"
else
    print_error "Backend API is not responding"
fi

# Check Frontend
frontend_port=${FRONTEND_PORT:-3000}
if curl -s http://localhost:$frontend_port >/dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend may still be starting up..."
fi

# Display access information
echo
echo "🎉 Setup complete!"
echo
echo "Access your D&D Note-Taking application:"
echo "  📱 Web Interface: http://localhost:${FRONTEND_PORT:-3000}"
echo "  🔌 API Documentation: http://localhost:${BACKEND_PORT:-8001}/docs"
echo "  🗄️  MongoDB: localhost:${MONGO_PORT:-27017}"
echo
echo "Default login credentials:"
echo "  👤 Username: admin"
echo "  🔑 Password: admin"
echo
echo "Useful commands:"
echo "  📋 View logs: docker-compose logs -f"
echo "  🔄 Restart: docker-compose restart"
echo "  🛑 Stop: docker-compose down"
echo "  🗑️  Clean reset: docker-compose down -v"
echo

# Optional: Open browser
if command -v open &> /dev/null; then
    read -p "Open application in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:${FRONTEND_PORT:-3000}
    fi
elif command -v xdg-open &> /dev/null; then
    read -p "Open application in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:${FRONTEND_PORT:-3000}
    fi
fi

print_success "D&D Note-Taking Application is ready to use!"

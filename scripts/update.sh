#!/bin/bash

# D&D Note-Taking Application - Update Script
# This script updates the application to the latest version

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

print_status "🎲 Updating D&D Note-Taking Application..."

# Create backup before update
print_status "Creating backup before update..."
./scripts/backup.sh

# Pull latest changes
if [ -d ".git" ]; then
    print_status "Pulling latest changes from git..."
    git pull origin main
    print_success "Code updated"
else
    print_warning "Not a git repository. Please manually update the code."
fi

# Stop services
print_status "Stopping services..."
docker-compose down

# Rebuild images
print_status "Rebuilding Docker images..."
docker-compose build --no-cache

# Start services
print_status "Starting updated services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 15

# Health check
print_status "Performing health check..."

backend_port=${BACKEND_PORT:-8001}
frontend_port=${FRONTEND_PORT:-3000}

# Check backend
if curl -s http://localhost:$backend_port/api/ >/dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_error "Backend health check failed"
    print_error "Check logs: docker-compose logs backend"
    exit 1
fi

# Check frontend
if curl -s http://localhost:$frontend_port >/dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend may still be starting up..."
fi

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    print_success "MongoDB is healthy"
else
    print_error "MongoDB health check failed"
    print_error "Check logs: docker-compose logs mongodb"
fi

echo
print_success "✅ Update completed successfully!"
echo
echo "Your D&D Note-Taking application has been updated!"
echo "  📱 Web Interface: http://localhost:$frontend_port"
echo "  🔌 API Documentation: http://localhost:$backend_port/docs"
echo
print_warning "If you experience any issues, you can restore from the backup created before update"
echo "Backup location: ./backups/"

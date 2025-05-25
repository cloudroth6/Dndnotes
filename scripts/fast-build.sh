#!/bin/bash

# D&D Note-Taking Application - Fast Build Script
# This script optimizes the build process for faster development

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "Docker Compose is not available"
    exit 1
fi

print_status "🚀 Fast build for D&D Note-Taking Application"

# Check what needs to be built
BUILD_FRONTEND=false
BUILD_BACKEND=false
BUILD_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend)
            BUILD_FRONTEND=true
            shift
            ;;
        --backend)
            BUILD_BACKEND=true
            shift
            ;;
        --all)
            BUILD_ALL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--frontend] [--backend] [--all]"
            echo "  --frontend  Build only frontend"
            echo "  --backend   Build only backend"
            echo "  --all       Build all services"
            echo "  (no args)   Interactive mode"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Interactive mode if no arguments
if [ "$BUILD_ALL" = false ] && [ "$BUILD_FRONTEND" = false ] && [ "$BUILD_BACKEND" = false ]; then
    echo "What would you like to build?"
    echo "1) Frontend only (faster)"
    echo "2) Backend only (faster)"  
    echo "3) All services"
    echo "4) Cancel"
    read -p "Choose option (1-4): " choice
    
    case $choice in
        1)
            BUILD_FRONTEND=true
            ;;
        2)
            BUILD_BACKEND=true
            ;;
        3)
            BUILD_ALL=true
            ;;
        4)
            echo "Cancelled"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

# Stop services before building
print_status "Stopping services..."
$DOCKER_COMPOSE_CMD down

# Build services
if [ "$BUILD_ALL" = true ]; then
    print_status "Building all services..."
    $DOCKER_COMPOSE_CMD build --no-cache
elif [ "$BUILD_FRONTEND" = true ]; then
    print_status "Building frontend only..."
    $DOCKER_COMPOSE_CMD build frontend --no-cache
elif [ "$BUILD_BACKEND" = true ]; then
    print_status "Building backend only..."
    $DOCKER_COMPOSE_CMD build backend --no-cache
fi

print_success "Build completed!"

# Start services
print_status "Starting services..."
$DOCKER_COMPOSE_CMD up -d

# Wait for services
print_status "Waiting for services to start..."
sleep 10

# Quick health check
print_status "Checking service health..."

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend may still be starting..."
fi

if curl -s http://localhost:8001/api/ >/dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_warning "Backend may still be starting..."
fi

echo
print_success "✅ Fast build completed!"
echo "  📱 Frontend: http://localhost:3000"
echo "  🔌 Backend: http://localhost:8001/docs"
echo
echo "💡 Tips for faster builds:"
echo "  • Use --frontend or --backend flags to build only what changed"
echo "  • .dockerignore files exclude unnecessary files"
echo "  • User creation moved early in Dockerfile"
echo "  • Use 'make logs' to see detailed logs"
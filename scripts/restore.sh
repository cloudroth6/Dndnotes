#!/bin/bash

# D&D Note-Taking Application - Restore Script
# This script restores backups of your campaign data

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

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Check if backup file is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <backup_file.tar.gz>"
    echo
    echo "Available backups:"
    ls -la ./backups/dnd_notes_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Source environment variables
source .env 2>/dev/null || true

DB_NAME=${DB_NAME:-dnd_notes}
MONGO_USER=${MONGO_ROOT_USERNAME:-admin}
MONGO_PASS=${MONGO_ROOT_PASSWORD:-password123}

print_warning "This will restore data from: $BACKUP_FILE"
print_warning "This will OVERWRITE existing campaign data!"
read -p "Are you sure you want to continue? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Restore cancelled"
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

print_status "Extracting backup archive..."
tar -xzf "$BACKUP_FILE"

# Check if services are running
if ! $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
    print_error "Docker services are not running. Please start them first:"
    echo "  $DOCKER_COMPOSE_CMD up -d"
    exit 1
fi

# Restore database
if [ -f backup_*.tar.gz ]; then
    print_status "Restoring MongoDB database..."
    
    # Extract database backup
    tar -xzf backup_*.tar.gz
    
    # Copy to container
    docker cp backup_*/ $($DOCKER_COMPOSE_CMD ps -q mongodb):/tmp/restore/
    
    # Drop existing database (with confirmation)
    print_warning "Dropping existing database: $DB_NAME"
    $DOCKER_COMPOSE_CMD exec -T mongodb mongosh \
        --username $MONGO_USER \
        --password $MONGO_PASS \
        --authenticationDatabase admin \
        --eval "db.getSiblingDB('$DB_NAME').dropDatabase()"
    
    # Restore database
    $DOCKER_COMPOSE_CMD exec -T mongodb mongorestore \
        --username $MONGO_USER \
        --password $MONGO_PASS \
        --authenticationDatabase admin \
        --db $DB_NAME \
        /tmp/restore/$DB_NAME
    
    print_success "Database restored successfully"
fi

# Restore application data (if JSON exports are available)
if [ -f sessions_*.json ] && [ -f npcs_*.json ]; then
    print_status "Application data exports found, but database restore takes precedence"
    print_status "JSON exports can be used for manual data verification if needed"
fi

# Cleanup
cd /
rm -rf $TEMP_DIR

# Restart application services
print_status "Restarting application services..."
$DOCKER_COMPOSE_CMD restart backend frontend

# Wait for services
sleep 5

# Verify restore
print_status "Verifying restore..."
backend_port=${BACKEND_PORT:-8001}

if curl -s -u admin:admin http://localhost:$backend_port/api/sessions >/dev/null 2>&1; then
    print_success "Backend is responding after restore"
else
    print_error "Backend is not responding after restore"
    exit 1
fi

echo
print_success "✅ Restore completed successfully!"
echo
echo "Your D&D campaign data has been restored from:"
echo "  📁 $BACKUP_FILE"
echo
echo "Access your restored application:"
echo "  📱 Web Interface: http://localhost:${FRONTEND_PORT:-3000}"
echo "  👤 Username: admin"
echo "  🔑 Password: admin"
echo
print_warning "Please verify your sessions and NPCs data in the application"

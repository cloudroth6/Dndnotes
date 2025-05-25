#!/bin/bash

# D&D Note-Taking Application - Backup Script
# This script creates backups of your campaign data

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
    print_error "Docker Compose is not available"
    exit 1
fi

# Source environment variables
source .env 2>/dev/null || true

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME=${DB_NAME:-dnd_notes}
MONGO_USER=${MONGO_ROOT_USERNAME:-admin}
MONGO_PASS=${MONGO_ROOT_PASSWORD:-password123}

# Create backup directory
mkdir -p $BACKUP_DIR

print_status "Creating backup of D&D campaign data..."

# Create database backup
print_status "Backing up MongoDB database..."
$DOCKER_COMPOSE_CMD exec -T mongodb mongodump \
    --username $MONGO_USER \
    --password $MONGO_PASS \
    --authenticationDatabase admin \
    --db $DB_NAME \
    --out /tmp/backup_$TIMESTAMP

# Copy backup from container to host
$DOCKER_COMPOSE_CMD exec -T mongodb tar -czf /tmp/backup_$TIMESTAMP.tar.gz -C /tmp backup_$TIMESTAMP

# Copy to host
docker cp $($DOCKER_COMPOSE_CMD ps -q mongodb):/tmp/backup_$TIMESTAMP.tar.gz $BACKUP_DIR/

print_success "Database backup saved: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# Create application data export
print_status "Creating application data export..."

# Export sessions
curl -s -u admin:admin http://localhost:${BACKEND_PORT:-8001}/api/sessions > $BACKUP_DIR/sessions_$TIMESTAMP.json

# Export NPCs
curl -s -u admin:admin http://localhost:${BACKEND_PORT:-8001}/api/npcs > $BACKUP_DIR/npcs_$TIMESTAMP.json

print_success "Application data exported"

# Create comprehensive backup archive
print_status "Creating comprehensive backup archive..."
cd $BACKUP_DIR
tar -czf dnd_notes_backup_$TIMESTAMP.tar.gz \
    backup_$TIMESTAMP.tar.gz \
    sessions_$TIMESTAMP.json \
    npcs_$TIMESTAMP.json

# Cleanup individual files
rm backup_$TIMESTAMP.tar.gz sessions_$TIMESTAMP.json npcs_$TIMESTAMP.json

print_success "Backup completed: $BACKUP_DIR/dnd_notes_backup_$TIMESTAMP.tar.gz"

# Cleanup old backups (keep last 10)
print_status "Cleaning up old backups..."
ls -t dnd_notes_backup_*.tar.gz | tail -n +11 | xargs -r rm
print_success "Old backups cleaned up (keeping last 10)"

echo
echo "✅ Backup process completed successfully!"
echo "📁 Backup location: $BACKUP_DIR/dnd_notes_backup_$TIMESTAMP.tar.gz"
echo
echo "To restore this backup:"
echo "  1. Stop the application: docker-compose down"
echo "  2. Run: ./scripts/restore.sh $BACKUP_DIR/dnd_notes_backup_$TIMESTAMP.tar.gz"
echo "  3. Start the application: docker-compose up -d"

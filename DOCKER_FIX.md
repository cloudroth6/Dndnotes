# Docker Setup Fix - Node.js Version Issue

## ❌ Error Description
```
ERROR [frontend 6/8] RUN yarn install --frozen-lockfile
error react-router-dom@7.5.1: The engine "node" is incompatible with this module. Expected version ">=20.0.0". Got "18.20.8"
```

## ✅ Solution Applied

The issue was that the frontend Docker image was using Node.js 18, but the `react-router-dom@7.5.1` package requires Node.js 20 or higher.

### Fixed Files:
1. **`frontend/Dockerfile`** - Updated to use Node.js 20
2. **`scripts/setup.sh`** - Added support for both `docker-compose` and `docker compose` commands
3. **`Makefile`** - Added automatic detection of Docker Compose command

## 🚀 How to Apply the Fix

### Option 1: Complete Rebuild (Recommended)
```bash
# Stop existing containers
docker-compose down
# OR
docker compose down

# Rebuild frontend with no cache
docker-compose build frontend --no-cache
# OR  
docker compose build frontend --no-cache

# Start services
docker-compose up -d
# OR
docker compose up -d
```

### Option 2: Using Make Commands
```bash
# Stop services
make stop

# Rebuild without cache
make build-no-cache

# Start services
make start
```

### Option 3: Complete Reset
```bash
# Remove everything and start fresh
docker-compose down -v --rmi all
# OR
docker compose down -v --rmi all

# Copy environment template
cp .env.example .env

# Run setup script
make setup
```

## 🔧 What Was Changed

### 1. Frontend Dockerfile
**Before:**
```dockerfile
FROM node:18-alpine
```

**After:**
```dockerfile
FROM node:20-alpine
```

### 2. Enhanced Scripts
- Added automatic detection of Docker Compose command (`docker-compose` vs `docker compose`)
- Updated all scripts to work with both legacy and modern Docker Compose installations
- Improved error handling and compatibility checks

## ✅ Verification

After applying the fix, verify everything works:

```bash
# Check service status
make ps

# Check health
make health

# View logs
make logs

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001/docs
```

## 🎯 Expected Result

- All services should start successfully
- Frontend builds without Node.js version errors
- Application accessible at configured ports
- All features working (sessions, NPCs, structured templates)

## 💡 Note

This fix ensures compatibility with modern React packages while maintaining full functionality of your D&D note-taking application. The Node.js 20 runtime provides better performance and security compared to Node.js 18.
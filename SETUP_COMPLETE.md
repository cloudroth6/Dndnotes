# D&D Note-Taking App - Complete Setup Guide

## 🎯 Quick Start (After Node.js Fix)

### 1. One-Command Setup
```bash
# Copy environment template and run setup
cp .env.example .env && make setup
```

### 2. Manual Setup
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env

# Stop any existing containers
docker-compose down
# OR
docker compose down

# Rebuild with Node.js 20 fix
docker-compose build --no-cache
# OR  
docker compose build --no-cache

# Start services
docker-compose up -d
# OR
docker compose up -d
```

## ✅ Verification Steps

### Check Service Status
```bash
# Using make commands
make ps
make health

# Using Docker Compose directly
docker-compose ps
# OR
docker compose ps
```

### Test Application Access
1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8001/docs  
3. **Login**: admin / admin

### Expected Results
- ✅ All services show "Up" status
- ✅ Frontend loads without errors
- ✅ Backend API documentation accessible
- ✅ Login works with admin/admin
- ✅ Can create both structured and free-form sessions
- ✅ NPC extraction functionality works

## 🔧 Available Commands

### Core Operations
```bash
make start              # Start all services
make stop               # Stop all services
make restart            # Restart all services
make logs               # View all logs
make build              # Rebuild images
make health             # Check service health
```

### Development
```bash
make dev                # Start with logs visible
make shell-backend      # Open backend shell
make shell-frontend     # Open frontend shell
make shell-mongodb      # Open MongoDB shell
```

### Data Management
```bash
make backup             # Create campaign data backup
make restore BACKUP=filename  # Restore from backup
make export-data        # Export sessions/NPCs as JSON
```

### Maintenance
```bash
make update             # Update to latest version
make clean              # Clean containers/volumes
make clean-all          # Deep clean (removes images too)
```

## 📊 Application Features Ready to Use

### ✅ Structured Session Templates
- **📅 Session Information**: Number, date, players
- **🎯 Session Goal**: What party aimed to achieve
- **⚔️ Combat Encounters**: Battles and outcomes
- **🎭 Roleplay Encounters**: Story interactions
- **👥 NPCs Encountered**: Character tracking
- **💰 Loot & Rewards**: Items and treasure
- **📝 Additional Notes**: Session insights
- **✨ Notable Moments**: Memorable quotes/events
- **🚀 Next Session Goals**: Planning ahead
- **🌍 Overarching Missions**: Long-term quests

### ✅ NPC Management
- Auto-extraction from session notes
- Character sheet format with all details
- History tracking across sessions
- Edit and update functionality

### ✅ Data Export/Import
- JSON export of all data
- Backup/restore functionality
- Session and NPC data preservation

## 🚨 Common Issues & Solutions

### Port Conflicts
```bash
# Check what's using a port
lsof -i :3000

# Change ports in .env
FRONTEND_PORT=8080
BACKEND_PORT=8081
```

### Services Not Starting
```bash
# Check logs
make logs

# Specific service logs
make logs-backend
make logs-frontend
make logs-mongodb

# Rebuild if needed
make build-no-cache
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

### Database Connection Issues
```bash
# Reset database
make stop
make clean
make start

# Check MongoDB logs
make logs-mongodb
```

## 📱 Using the Application

### Creating Your First Session
1. Login with admin/admin
2. Select "📋 Structured Template" 
3. Click "New Session"
4. Navigate through sections using tabs
5. Fill in session details
6. Save session

### Extracting NPCs
1. In any session notes, mention characters
2. Highlight character names
3. Click "Extract NPC" button
4. NPCs automatically appear in NPCs tab

### Viewing Session History
- Rich session cards show all data entered
- Color-coded mission statuses
- Quick overview of encounters, NPCs, loot

## 🎲 Ready for Your Campaign!

Your D&D Note-Taking application is now fully functional with:
- ✅ Professional session management
- ✅ Automatic NPC tracking  
- ✅ Rich text editing
- ✅ Data export/backup
- ✅ Responsive design
- ✅ Easy local hosting

**Start your campaign tracking today!**

---

## 📞 Need Help?

1. Check logs: `make logs`
2. Verify health: `make health` 
3. Review this guide
4. Check Docker/Docker Compose installation
5. Ensure ports are available

**Happy adventuring!** 🎲⚔️🧙‍♂️
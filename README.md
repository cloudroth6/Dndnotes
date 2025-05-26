# D&D Note-Taking System - Complete Administrator Guide

A comprehensive Dungeons & Dragons campaign management system with AI-powered NPC extraction, loot tracking, player attendance, and intelligent session note-taking.

## 🎯 **System Overview**

This D&D note-taking system provides:
- **🤖 AI-Powered NPC Extraction** using Ollama/Llama
- **💰 Intelligent Loot Management** with player inventory tracking
- **🧑‍🤝‍🧑 Player Attendance Tracking** with statistics
- **📋 Template-Based Session Management** for consistent note-taking
- **🎭 Rich Text Formatting** with live preview
- **📊 Comprehensive Campaign Analytics**

## 🏗️ **Architecture**

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **AI Engine**: Ollama (Local LLM)
- **Deployment**: Docker Compose

---

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Docker & Docker Compose
- 8GB+ RAM (recommended for Ollama)
- Git

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd dnd-notes-app
cp .env.example .env
```

### **2. Basic Configuration**
Edit `.env` file:
```env
# Required settings
COMPOSE_PROJECT_NAME=dnd-notes
FRONTEND_PORT=3000
BACKEND_PORT=8001
MONGO_PORT=27017

# Database credentials
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password123
DB_NAME=dnd_notes

# Backend URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

### **3. Start Core Services**
```bash
# Start without AI (basic functionality)
make start

# Or with full setup script
make setup
```

### **4. Access Application**
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Login**: admin / admin

---

## 🤖 **AI Integration Setup (Ollama/Llama)**

### **Step 1: Install Ollama**

#### **Option A: Linux/macOS**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

#### **Option B: Windows**
1. Download from https://ollama.ai/download
2. Run installer
3. Ollama starts automatically

#### **Option C: Docker (Recommended)**
```bash
# Run Ollama in Docker
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

# Verify running
docker ps | grep ollama
```

### **Step 2: Download AI Models**
```bash
# Download Llama2 (recommended for D&D)
ollama pull llama2

# Or smaller model for testing
ollama pull llama2:7b

# List available models
ollama list
```

### **Step 3: Test Ollama Installation**
```bash
# Test command line
ollama run llama2 "What is Dungeons and Dragons?"

# Test API
curl http://localhost:11434/api/tags

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Extract NPCs from: The party met Thorin the Blacksmith",
  "stream": false
}'
```

### **Step 4: Enable AI in D&D App**
Update `.env` file:
```env
# Enable Ollama
OLLAMA_ENABLED=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60
OLLAMA_TEMPERATURE=0.7
```

Restart application:
```bash
make restart
```

### **Step 5: Test AI Integration**
```bash
# Use automated test script
./scripts/test-ollama.sh

# Manual API test
curl -u admin:admin http://localhost:8001/api/admin/ollama/test
```

**Expected Response (AI Working):**
```json
{
  "status": "connected",
  "message": "Successfully connected to Ollama",
  "available_models": ["llama2"]
}
```

---

## 🔧 **System Administration**

### **Service Management**
```bash
# Start all services
make start

# Stop all services
make stop

# Restart services
make restart

# View logs
make logs

# Check service health
make health

# Service status
make ps
```

### **Database Management**
```bash
# Access MongoDB shell
make shell-mongodb

# Backup campaign data
make backup

# Restore from backup
make restore BACKUP=backup_filename.tar.gz

# Export data as JSON
make export-data
```

### **Updates and Maintenance**
```bash
# Update to latest version
make update

# Rebuild Docker images
make build-no-cache

# Clean up old containers
make clean

# Deep clean (removes images)
make clean-all
```

---

## 📋 **Feature Configuration**

### **Player Management Setup**

#### **1. Create Initial Players**
```bash
# Via API
curl -u admin:admin -X POST http://localhost:8001/api/players \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "character_name": "Lyralei the Archer", 
    "character_class": "Ranger",
    "character_level": 5,
    "notes": "Expert marksman and tracker"
  }'
```

#### **2. Test Player Features**
```bash
# List all players
curl -u admin:admin http://localhost:8001/api/players

# Get player attendance
curl -u admin:admin http://localhost:8001/api/players/{player_id}/attendance

# Get player loot
curl -u admin:admin http://localhost:8001/api/players/{player_id}/loot
```

### **AI Extraction Configuration**

#### **1. Customize NPC Extraction Prompt**
```bash
# Get current admin config
curl -u admin:admin http://localhost:8001/api/admin/config

# Update extraction prompts via admin interface
# (Frontend admin panel recommended)
```

#### **2. Test NPC Extraction**
```bash
curl -u admin:admin -X POST http://localhost:8001/api/extract-npcs-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "session_text": "The party met Thorin the Blacksmith, a gruff dwarf who forged them a +1 sword. Later they encountered Elara the Barmaid who gave them information about the dragon.",
    "session_id": "test-session-123"
  }'
```

#### **3. Test Loot Extraction**
```bash
curl -u admin:admin -X POST http://localhost:8001/api/extract-loot-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "session_text": "Alice found a Potion of Healing in the chest. Bob picked up the magical Flame Tongue sword worth 500 gold pieces.",
    "session_id": "test-session-123",
    "players": [
      {"id": "player-1", "name": "Alice", "character_name": "Lyralei"},
      {"id": "player-2", "name": "Bob", "character_name": "Thorek"}
    ]
  }'
```

### **Template Configuration**

The system uses structured session templates with these sections:
- **📅 Session Information** - Number, date, duration, DM, attendance
- **🎯 Session Goal & Summary** - Objectives and outcomes
- **⚔️ Combat Encounters** - Battles and conflicts
- **🎭 Roleplay Encounters** - Story interactions
- **👥 NPCs Encountered** - Character interactions (AI-extracted)
- **💰 Loot Found** - Items and treasure (AI-extracted)
- **📝 Session Notes** - Additional details
- **✨ Notable Moments** - Memorable quotes and events
- **🚀 Next Session Planning** - Future goals
- **🌍 Overarching Missions** - Long-term story arcs

---

## 🧪 **Testing & Validation**

### **Complete System Test**
```bash
# Run comprehensive test suite
./scripts/test-ollama.sh

# Test individual components
curl -u admin:admin http://localhost:8001/api/        # Backend
curl http://localhost:3000                            # Frontend
curl http://localhost:11434/api/tags                  # Ollama
```

### **Feature Testing Checklist**

#### **✅ Core Functionality**
- [ ] User can login (admin/admin)
- [ ] Sessions can be created and edited
- [ ] Rich text editor works with formatting
- [ ] Session cards display properly

#### **✅ Player Management**
- [ ] Players can be created with character details
- [ ] Player list displays correctly
- [ ] Attendance tracking works
- [ ] Player loot inventory accessible

#### **✅ AI Features (if Ollama enabled)**
- [ ] NPC extraction finds characters in session text
- [ ] NPCs have detailed information (race, class, personality)
- [ ] Loot extraction finds items and assigns to players
- [ ] Smart data merging prevents duplicates

#### **✅ Advanced Features**
- [ ] Session export works
- [ ] Data backup/restore functions
- [ ] Admin configuration accessible
- [ ] Attendance statistics calculate correctly

### **Performance Benchmarks**
- **Session Load Time**: < 2 seconds
- **AI Extraction Time**: < 30 seconds (depends on text length)
- **Database Queries**: < 500ms average
- **File Export**: < 5 seconds

---

## 🔐 **Security Configuration**

### **Production Settings**
Update `.env` for production:
```env
# Change default credentials
MONGO_ROOT_PASSWORD=your-secure-database-password
ADMIN_PASSWORD=your-secure-admin-password

# Use specific backend URL
REACT_APP_BACKEND_URL=https://yourdomain.com

# Environment settings
NODE_ENV=production
ENVIRONMENT=production
```

### **SSL/HTTPS Setup**
```bash
# Start with nginx reverse proxy
make start-with-nginx

# Configure SSL certificates in nginx/ssl/
# Update nginx.conf for HTTPS
```

### **Firewall Configuration**
```bash
# Required open ports:
# 3000 - Frontend (HTTP)
# 8001 - Backend API  
# 27017 - MongoDB (internal only)
# 11434 - Ollama (internal only)
# 80/443 - Nginx (if used)
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Services Won't Start**
```bash
# Check port conflicts
lsof -i :3000
lsof -i :8001

# Check Docker
docker system df
docker system prune

# Restart everything
make stop && make start
```

#### **Ollama Connection Failed**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
# or
docker restart ollama

# Check model availability
ollama list
```

#### **Database Issues**
```bash
# Check MongoDB logs
make logs-mongodb

# Reset database
make stop
make clean
make start

# Restore from backup
make restore BACKUP=filename.tar.gz
```

#### **Frontend Not Loading**
```bash
# Check frontend logs
make logs-frontend

# Clear browser cache
# Check backend connectivity
curl -u admin:admin http://localhost:8001/api/
```

### **Performance Issues**
```bash
# Monitor resource usage
make monitor

# Check disk space
df -h

# Clean up Docker
docker system prune -a
```

### **Log Locations**
```bash
# Application logs
make logs

# System logs
sudo journalctl -u docker

# Backend logs specifically
tail -f /var/log/supervisor/backend.*.log
```

---

## 📚 **API Reference**

### **Authentication**
All API endpoints require HTTP Basic Auth:
- **Username**: admin
- **Password**: admin (change in production)

### **Core Endpoints**

#### **Player Management**
```bash
GET    /api/players                    # List all players
POST   /api/players                    # Create player
GET    /api/players/{id}               # Get player details
PUT    /api/players/{id}               # Update player
DELETE /api/players/{id}               # Delete player
GET    /api/players/{id}/loot          # Get player inventory
GET    /api/players/{id}/attendance    # Get attendance stats
```

#### **Session Management** 
```bash
GET    /api/sessions                   # List all sessions
POST   /api/sessions                   # Create session
GET    /api/sessions/{id}              # Get session details
PUT    /api/sessions/{id}              # Update session
DELETE /api/sessions/{id}              # Delete session
GET    /api/sessions/{id}/export       # Export session data
```

#### **NPC Management**
```bash
GET    /api/npcs                       # List all NPCs
POST   /api/npcs                       # Create NPC
GET    /api/npcs/{id}                  # Get NPC details
PUT    /api/npcs/{id}                  # Update NPC
DELETE /api/npcs/{id}                  # Delete NPC
POST   /api/extract-npcs-advanced      # AI NPC extraction
```

#### **Loot Management**
```bash
GET    /api/loot                       # List all loot
POST   /api/loot                       # Create loot item
GET    /api/loot/{id}                  # Get loot details
PUT    /api/loot/{id}                  # Update loot item
DELETE /api/loot/{id}                  # Delete loot item
POST   /api/extract-loot-advanced      # AI loot extraction
```

#### **Admin Configuration**
```bash
GET    /api/admin/config               # Get admin settings
POST   /api/admin/config               # Update admin settings
GET    /api/admin/ollama/test          # Test Ollama connection
GET    /api/admin/ollama/config        # Get Ollama settings
```

### **API Documentation**
Access interactive API docs at: http://localhost:8001/docs

---

## 🎯 **Best Practices**

### **Regular Maintenance**
```bash
# Weekly tasks
make backup                    # Backup campaign data
make update                   # Update to latest version
make health                   # Check system health

# Monthly tasks
make clean                    # Clean up old containers
docker system prune -a       # Deep clean Docker
```

### **Campaign Management**
1. **Setup Players First** - Create all campaign players before sessions
2. **Use Templates Consistently** - Stick to structured session format
3. **Leverage AI Extraction** - Let AI handle NPC and loot detection
4. **Regular Backups** - Backup before major sessions
5. **Monitor Attendance** - Track player participation statistics

### **Performance Optimization**
1. **Ollama Model Selection** - Use llama2:7b for faster responses
2. **Session Text Length** - Keep sessions under 10,000 characters for optimal AI processing
3. **Regular Cleanup** - Clean old Docker containers and logs
4. **Resource Monitoring** - Monitor RAM usage with Ollama

---

## 📞 **Support**

### **Getting Help**
1. Check this README for common solutions
2. Review logs: `make logs`
3. Test individual components
4. Check GitHub issues
5. Review Docker and Ollama documentation

### **Contributing**
1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

### **Reporting Issues**
Include in bug reports:
- System information (OS, Docker version)
- Error logs (`make logs`)
- Steps to reproduce
- Expected vs actual behavior

---

## 🎲 **Ready to Run Your Campaign!**

Your D&D note-taking system is now fully configured with:

- ✅ **AI-Powered Intelligence** for automatic NPC and loot extraction
- ✅ **Professional Templates** for consistent session documentation  
- ✅ **Player Management** with attendance tracking and inventory
- ✅ **Rich Text Editing** with live preview and formatting
- ✅ **Comprehensive APIs** for all campaign data
- ✅ **Backup & Export** for data protection
- ✅ **Docker Deployment** for easy scaling and portability

**Start your epic campaign tracking today!** 🧙‍♂️⚔️✨

---

*Last Updated: 2025 - Version 2.0 with AI Integration*
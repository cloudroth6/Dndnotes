# D&D Note-Taking System - Quick Setup Checklist

## 🚀 **Admin Quick Start Checklist**

### **Phase 1: Basic Setup (Required)**
- [ ] Install Docker & Docker Compose
- [ ] Clone repository
- [ ] Copy `.env.example` to `.env`
- [ ] Update basic configuration in `.env`
- [ ] Run `make setup` or `make start`
- [ ] Verify access at http://localhost:3000
- [ ] Test login with admin/admin

### **Phase 2: AI Integration (Optional but Recommended)**
- [ ] Install Ollama (Linux/macOS/Windows/Docker)
- [ ] Download AI model: `ollama pull llama2`
- [ ] Test Ollama: `curl http://localhost:11434/api/tags`
- [ ] Enable in `.env`: `OLLAMA_ENABLED=true`
- [ ] Restart app: `make restart`
- [ ] Test AI: `./scripts/test-ollama.sh`

### **Phase 3: System Validation**
- [ ] Create test players via API
- [ ] Create structured session
- [ ] Test NPC extraction
- [ ] Test loot extraction
- [ ] Verify attendance tracking
- [ ] Test data backup: `make backup`

### **Phase 4: Production Preparation**
- [ ] Change default passwords in `.env`
- [ ] Configure SSL/HTTPS (if needed)
- [ ] Set up regular backup schedule
- [ ] Configure monitoring/alerts
- [ ] Test disaster recovery procedures

## 🔧 **Essential Commands**

```bash
# Basic operations
make start          # Start all services
make stop           # Stop all services
make restart        # Restart services
make logs           # View all logs
make health         # Check system health

# AI testing
./scripts/test-ollama.sh    # Test Ollama integration

# Data management
make backup         # Backup campaign data
make export-data    # Export as JSON

# Maintenance
make update         # Update system
make clean          # Clean containers
```

## 📞 **Quick Support**

**Check these first:**
1. `make health` - Overall system status
2. `make logs` - Error messages
3. `./scripts/test-ollama.sh` - AI functionality
4. Browser dev tools - Frontend issues

**Common fixes:**
- Port conflicts: Change ports in `.env`
- Service issues: `make restart`
- Database problems: `make clean && make start`
- AI not working: Check Ollama installation

## 🎯 **Success Criteria**

Your system is ready when:
- ✅ Web interface loads at http://localhost:3000
- ✅ Login works with admin/admin
- ✅ Sessions can be created and saved
- ✅ Players can be managed
- ✅ AI extraction works (if Ollama enabled)
- ✅ Data can be backed up and restored

**Time to complete setup: 15-30 minutes** (depending on AI setup)

---

*For detailed instructions, see the main README.md file*
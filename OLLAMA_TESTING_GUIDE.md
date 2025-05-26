# Ollama Testing Guide for D&D Note-Taking App

## 🚀 Step 1: Install Ollama

### **Option A: Linux/macOS**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

### **Option B: Windows**
1. Download from https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

### **Option C: Docker (Recommended for consistency)**
```bash
# Run Ollama in Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Check if running
docker ps | grep ollama
```

## 🧪 Step 2: Test Ollama Directly

### **Download a Model**
```bash
# Download llama2 (recommended for D&D)
ollama pull llama2

# Or try a smaller model for testing
ollama pull llama2:7b

# List available models
ollama list
```

### **Test Basic Functionality**
```bash
# Test Ollama via command line
ollama run llama2 "Hello, tell me about D&D"

# Test API directly
curl http://localhost:11434/api/tags

# Test generation API
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "What is Dungeons and Dragons?",
  "stream": false
}'
```

## ⚙️ Step 3: Configure Your D&D App

### **Update Environment Variables**
Edit your `.env` file:
```bash
# Enable Ollama
OLLAMA_ENABLED=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60
OLLAMA_TEMPERATURE=0.7
```

### **Restart Your Backend**
```bash
# Using make commands
make restart

# Or using docker-compose directly
docker-compose restart backend
# OR
docker compose restart backend
```

## 🔍 Step 4: Test Through D&D App API

### **Test 1: Check Ollama Connection**
```bash
# Test connection through your app
curl -u admin:admin http://localhost:8001/api/admin/ollama/test

# Expected successful response:
{
  "status": "connected",
  "message": "Successfully connected to Ollama",
  "available_models": ["llama2"]
}
```

### **Test 2: Get Current Configuration**
```bash
# Check current Ollama config
curl -u admin:admin http://localhost:8001/api/admin/ollama/config

# Expected response:
{
  "enabled": true,
  "host": "http://localhost:11434",
  "model": "llama2",
  "timeout": 60,
  "temperature": 0.7
}
```

### **Test 3: Test NPC Extraction**
```bash
# Test advanced NPC extraction
curl -u admin:admin -X POST http://localhost:8001/api/extract-npcs-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "session_text": "The party met Thorin the Blacksmith in his forge. He was a stout dwarf with a gruff manner, but he helped them by forging a magical sword. Later, they encountered Elara the Barmaid at the tavern who gave them information about the dragon.",
    "session_id": "test-session-123",
    "use_ollama": true
  }'
```

## 📊 Step 5: Expected Test Results

### **✅ Successful Ollama Integration:**
```json
{
  "npcs_processed": 2,
  "results": [
    {
      "action": "created",
      "npc": {
        "name": "Thorin the Blacksmith",
        "race": "Dwarf",
        "class_role": "Blacksmith",
        "location": "Forge",
        "personality_traits": "Gruff manner",
        "interactions": "Forged a magical sword for the party",
        "loot_given": "Magical sword",
        "status": "alive"
      },
      "extraction_method": "ollama_advanced"
    },
    {
      "action": "created", 
      "npc": {
        "name": "Elara the Barmaid",
        "class_role": "Barmaid",
        "location": "Tavern",
        "interactions": "Gave information about the dragon"
      },
      "extraction_method": "ollama_advanced"
    }
  ],
  "ollama_enabled": true
}
```

### **❌ Ollama Not Working (Fallback):**
```json
{
  "npcs_processed": 2,
  "results": [
    {
      "action": "created",
      "npc": {
        "name": "Thorin the Blacksmith",
        "interactions": "Mentioned in session text",
        "additional_notes": "Extracted using rule-based detection"
      },
      "extraction_method": "rule_based"
    }
  ],
  "ollama_enabled": false
}
```

## 🛠️ Troubleshooting

### **Issue 1: Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If this fails, restart Ollama:
ollama serve

# Or restart Docker container:
docker restart ollama
```

### **Issue 2: Model Not Found**
```bash
# Check available models
ollama list

# Download the model if missing
ollama pull llama2
```

### **Issue 3: Backend Can't Connect**
```bash
# Check backend logs
make logs-backend

# Check if environment variables are loaded
curl -u admin:admin http://localhost:8001/api/admin/ollama/config
```

### **Issue 4: Timeout Errors**
```bash
# Increase timeout in .env
OLLAMA_TIMEOUT=120

# Restart backend
make restart
```

## 🔧 Quick Debugging Commands

### **Check Everything is Running:**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check D&D App Backend
curl -u admin:admin http://localhost:8001/api/

# Check Integration
curl -u admin:admin http://localhost:8001/api/admin/ollama/test
```

### **View Logs:**
```bash
# Backend logs
make logs-backend

# All services
make logs

# Ollama logs (if using Docker)
docker logs ollama
```

## 🎯 Testing Different Models

### **Try Different Models:**
```bash
# Download other models
ollama pull mistral
ollama pull codellama
ollama pull llama2:13b

# Update your .env to test different models
OLLAMA_MODEL=mistral
```

### **Test Model Performance:**
```bash
# Test each model with the same prompt
curl -u admin:admin -X POST http://localhost:8001/api/extract-npcs-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "session_text": "Your test session text here...",
    "session_id": "model-test-123"
  }'
```

## ✅ Success Indicators

You'll know Ollama is working correctly when:

1. **✅ Connection Test Passes**
   - `/api/admin/ollama/test` returns `"status": "connected"`

2. **✅ Advanced Extraction Works**
   - NPCs have detailed information (race, class, personality, etc.)
   - `extraction_method` shows `"ollama_advanced"`

3. **✅ Rich NPC Data**
   - Multiple fields populated automatically
   - Intelligent parsing of session text
   - Structured JSON responses

4. **✅ Better Than Rule-Based**
   - More NPCs detected
   - More detailed information extracted
   - Better understanding of context

## 🎲 Ready to Use!

Once Ollama is working, your D&D app will:
- **Automatically extract detailed NPCs** from session text
- **Populate comprehensive character sheets** 
- **Understand context and relationships**
- **Provide intelligent data merging**

Your NPC extraction will go from basic name detection to full character analysis! 🧙‍♂️⚔️
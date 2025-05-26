#!/bin/bash

# Ollama Testing Script for D&D Note-Taking App
# This script tests Ollama integration step by step

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

echo "🎲 D&D Note-Taking App - Ollama Integration Test"
echo "================================================"

# Test 1: Check if Ollama is running
print_status "Testing Ollama service connection..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    print_success "Ollama service is running on localhost:11434"
    
    # Get available models
    models=$(curl -s http://localhost:11434/api/tags | grep '"name"' | cut -d'"' -f4 || echo "")
    if [ -n "$models" ]; then
        print_success "Available Ollama models:"
        echo "$models" | while read model; do
            echo "  - $model"
        done
    else
        print_warning "No models found. You may need to download a model:"
        echo "  ollama pull llama2"
    fi
else
    print_error "Ollama service is not running or not accessible"
    echo ""
    echo "To install and start Ollama:"
    echo "  1. Visit: https://ollama.ai/download"
    echo "  2. Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  3. Start: ollama serve"
    echo "  4. Download model: ollama pull llama2"
    exit 1
fi

echo ""

# Test 2: Check D&D App Backend
print_status "Testing D&D App backend connection..."
if curl -s -u admin:admin http://localhost:8001/api/ >/dev/null 2>&1; then
    print_success "D&D App backend is running"
else
    print_error "D&D App backend is not accessible"
    echo "Make sure your app is running: make start"
    exit 1
fi

echo ""

# Test 3: Check Ollama integration in D&D App
print_status "Testing Ollama integration in D&D App..."
response=$(curl -s -u admin:admin http://localhost:8001/api/admin/ollama/test 2>/dev/null || echo "")

if [ -n "$response" ]; then
    status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    message=$(echo "$response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$status" = "connected" ]; then
        print_success "Ollama integration is working!"
        print_success "Message: $message"
        
        # Extract available models
        models=$(echo "$response" | grep -o '"available_models":\[[^]]*\]' | sed 's/"available_models":\[//; s/\]//; s/"//g')
        if [ -n "$models" ]; then
            print_success "Models available through integration: $models"
        fi
    else
        print_warning "Ollama integration status: $status"
        print_warning "Message: $message"
    fi
else
    print_error "Failed to test Ollama integration"
fi

echo ""

# Test 4: Check current configuration
print_status "Checking Ollama configuration..."
config=$(curl -s -u admin:admin http://localhost:8001/api/admin/ollama/config 2>/dev/null || echo "")

if [ -n "$config" ]; then
    enabled=$(echo "$config" | grep -o '"enabled":[^,}]*' | cut -d':' -f2)
    host=$(echo "$config" | grep -o '"host":"[^"]*"' | cut -d'"' -f4)
    model=$(echo "$config" | grep -o '"model":"[^"]*"' | cut -d'"' -f4)
    
    print_success "Configuration loaded:"
    echo "  - Enabled: $enabled"
    echo "  - Host: $host"
    echo "  - Model: $model"
    
    if [ "$enabled" = "true" ]; then
        print_success "Ollama is enabled in D&D App"
    else
        print_warning "Ollama is disabled in D&D App"
        echo "To enable, update your .env file:"
        echo "  OLLAMA_ENABLED=true"
        echo "  OLLAMA_HOST=http://localhost:11434"
        echo "  OLLAMA_MODEL=llama2"
        echo "Then restart: make restart"
    fi
else
    print_error "Failed to retrieve Ollama configuration"
fi

echo ""

# Test 5: Test NPC extraction
print_status "Testing advanced NPC extraction..."

test_session_text="The party entered the tavern and met Gareth the Innkeeper, a friendly human who offered them rooms for the night. Later, they encountered Shadowbane the Assassin, a mysterious elf who challenged them to a duel. The wizard Merlin the Wise appeared and helped resolve the conflict peacefully."

extraction_response=$(curl -s -u admin:admin -X POST http://localhost:8001/api/extract-npcs-advanced \
    -H "Content-Type: application/json" \
    -d "{
        \"session_text\": \"$test_session_text\",
        \"session_id\": \"test-$(date +%s)\",
        \"use_ollama\": true
    }" 2>/dev/null || echo "")

if [ -n "$extraction_response" ]; then
    npcs_processed=$(echo "$extraction_response" | grep -o '"npcs_processed":[0-9]*' | cut -d':' -f2)
    ollama_enabled=$(echo "$extraction_response" | grep -o '"ollama_enabled":[^,}]*' | cut -d':' -f2)
    
    if [ "$npcs_processed" -gt 0 ]; then
        print_success "NPC extraction successful!"
        print_success "NPCs processed: $npcs_processed"
        print_success "Ollama enabled: $ollama_enabled"
        
        # Check extraction method
        if echo "$extraction_response" | grep -q "ollama_advanced"; then
            print_success "✨ Using advanced Ollama extraction!"
            echo "NPCs extracted with detailed information from Ollama LLM"
        elif echo "$extraction_response" | grep -q "rule_based"; then
            print_warning "Using fallback rule-based extraction"
            echo "Ollama may not be fully working, but fallback is functional"
        fi
    else
        print_warning "No NPCs were extracted from test text"
    fi
else
    print_error "Failed to test NPC extraction"
fi

echo ""

# Summary
echo "🎯 Test Summary"
echo "==============="

# Check overall status
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && \
   curl -s -u admin:admin http://localhost:8001/api/admin/ollama/test | grep -q '"status":"connected"'; then
    print_success "✅ Ollama integration is fully working!"
    echo ""
    echo "🚀 You can now use advanced NPC extraction in your D&D app:"
    echo "  1. Create or edit a session"
    echo "  2. Add detailed session notes with character mentions"
    echo "  3. Use the 'Extract and Update NPCs' button"
    echo "  4. Watch as Ollama intelligently extracts detailed character information!"
    echo ""
    echo "💡 Tip: The more descriptive your session text, the better NPCs Ollama can extract!"
else
    print_warning "⚠️  Ollama integration needs attention"
    echo ""
    echo "🔧 Quick fixes to try:"
    echo "  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  2. Start Ollama: ollama serve"
    echo "  3. Download model: ollama pull llama2"
    echo "  4. Update .env: OLLAMA_ENABLED=true"
    echo "  5. Restart app: make restart"
    echo ""
    echo "📚 For detailed instructions, see: OLLAMA_TESTING_GUIDE.md"
fi

echo ""
echo "🎲 Happy adventuring!"
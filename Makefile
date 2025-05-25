# D&D Note-Taking Application - Makefile
# Convenient commands for managing the application

# Detect Docker Compose command
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null)
ifndef DOCKER_COMPOSE
	DOCKER_COMPOSE := docker compose
endif

.PHONY: help setup start stop restart logs build backup restore update clean dev

# Default target
help: ## Show this help message
	@echo "D&D Note-Taking Application - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create .env and start application
	@echo "🎲 Setting up D&D Note-Taking Application..."
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

start: ## Start all services
	@echo "🚀 Starting services..."
	@$(DOCKER_COMPOSE) up -d

start-with-nginx: ## Start all services including Nginx reverse proxy
	@echo "🚀 Starting services with Nginx..."
	@$(DOCKER_COMPOSE) --profile nginx up -d

stop: ## Stop all services
	@echo "🛑 Stopping services..."
	@$(DOCKER_COMPOSE) down

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	@$(DOCKER_COMPOSE) restart

logs: ## View logs from all services
	@$(DOCKER_COMPOSE) logs -f

logs-backend: ## View backend logs only
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## View frontend logs only
	@$(DOCKER_COMPOSE) logs -f frontend

logs-mongodb: ## View MongoDB logs only
	@$(DOCKER_COMPOSE) logs -f mongodb

build: ## Rebuild all Docker images
	@echo "🔨 Building Docker images..."
	@$(DOCKER_COMPOSE) build

build-no-cache: ## Rebuild all Docker images without cache
	@echo "🔨 Building Docker images (no cache)..."
	@$(DOCKER_COMPOSE) build --no-cache

dev: ## Start in development mode with logs visible
	@echo "🛠️ Starting in development mode..."
	@$(DOCKER_COMPOSE) up

backup: ## Create backup of campaign data
	@echo "💾 Creating backup..."
	@chmod +x scripts/backup.sh
	@./scripts/backup.sh

restore: ## Restore from backup (usage: make restore BACKUP=filename)
	@echo "📥 Restoring from backup..."
	@chmod +x scripts/restore.sh
	@./scripts/restore.sh $(BACKUP)

update: ## Update application to latest version
	@echo "⬆️ Updating application..."
	@chmod +x scripts/update.sh
	@./scripts/update.sh

clean: ## Clean up Docker containers and volumes
	@echo "🧹 Cleaning up..."
	@$(DOCKER_COMPOSE) down -v
	@docker system prune -f

clean-all: ## Clean up everything including images
	@echo "🧹 Deep cleaning..."
	@$(DOCKER_COMPOSE) down -v --rmi all
	@docker system prune -af

ps: ## Show status of all services
	@$(DOCKER_COMPOSE) ps

shell-backend: ## Open shell in backend container
	@$(DOCKER_COMPOSE) exec backend bash

shell-frontend: ## Open shell in frontend container
	@$(DOCKER_COMPOSE) exec frontend sh

shell-mongodb: ## Open MongoDB shell
	@$(DOCKER_COMPOSE) exec mongodb mongosh -u admin -p password123

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo "Backend API:"
	@curl -s http://localhost:8001/api/ && echo " ✅ Healthy" || echo " ❌ Unhealthy"
	@echo "Frontend:"
	@curl -s http://localhost:3000 >/dev/null && echo " ✅ Healthy" || echo " ❌ Unhealthy"
	@echo "MongoDB:"
	@$(DOCKER_COMPOSE) exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1 && echo " ✅ Healthy" || echo " ❌ Unhealthy"

# Development helpers
install-backend: ## Install backend dependencies
	@$(DOCKER_COMPOSE) exec backend pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	@$(DOCKER_COMPOSE) exec frontend yarn install

test-backend: ## Run backend tests
	@$(DOCKER_COMPOSE) exec backend python -m pytest

test-frontend: ## Run frontend tests
	@$(DOCKER_COMPOSE) exec frontend yarn test

# Quick actions
quick-restart: stop start ## Quick restart (stop + start)

quick-rebuild: stop build start ## Quick rebuild (stop + build + start)

# Environment management
env-copy: ## Copy .env.example to .env
	@cp .env.example .env
	@echo "📋 Environment file copied. Edit .env to customize settings."

env-show: ## Show current environment variables
	@echo "Current environment configuration:"
	@cat .env 2>/dev/null || echo "No .env file found. Run 'make env-copy' first."

# Data management
export-data: ## Export all data as JSON
	@mkdir -p exports
	@curl -s -u admin:admin http://localhost:8001/api/sessions > exports/sessions_$(shell date +%Y%m%d_%H%M%S).json
	@curl -s -u admin:admin http://localhost:8001/api/npcs > exports/npcs_$(shell date +%Y%m%d_%H%M%S).json
	@echo "📤 Data exported to exports/ directory"

# Production helpers
prod-start: ## Start in production mode with nginx
	@ENVIRONMENT=production $(DOCKER_COMPOSE) --profile nginx up -d

prod-logs: ## View production logs
	@$(DOCKER_COMPOSE) --profile nginx logs -f

# Monitoring
monitor: ## Monitor resource usage
	@watch -n 2 'docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"'

.PHONY: help dev up down restart logs logs-back logs-front logs-db logs-redis shell shell-db shell-redis migrate makemigrations createsuperuser test test-front clean rebuild reset build ps health

# Color output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# Docker Compose command detection
# Try docker compose (v2) first, fallback to docker-compose (v1)
DOCKER_COMPOSE := $(shell docker compose version > /dev/null 2>&1 && echo "docker compose" || echo "docker-compose")
DOCKER_DIR := docker

help:  ## Show this help message
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(CYAN)  EduLite Docker Development Commands$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Using: $(DOCKER_COMPOSE)$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# -------------------------------------------------------------------
# Service Management
# -------------------------------------------------------------------

dev:  ## Start all services in foreground (with logs)
	@echo "$(CYAN)Starting EduLite development environment...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) up

up:  ## Start all services in background
	@echo "$(CYAN)Starting EduLite services in background...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo ""
	@echo "$(CYAN)Access the application:$(NC)"
	@echo "  Frontend: $(GREEN)http://localhost:5173$(NC)"
	@echo "  Backend:  $(GREEN)http://localhost:8000$(NC)"
	@echo "  API Docs: $(GREEN)http://localhost:8000/redoc/$(NC)"
	@echo "  API Swagger: $(GREEN)http://localhost:8000/swagger/$(NC)"
	@echo ""
	@echo "$(CYAN)View logs with:$(NC) make logs"
	@echo "$(CYAN)Stop services with:$(NC) make down"

down:  ## Stop all services
	@echo "$(YELLOW)Stopping EduLite services...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart:  ## Restart all services
	@echo "$(CYAN)Restarting EduLite services...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

stop:  ## Stop services without removing containers
	@echo "$(YELLOW)Stopping services...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) stop

start:  ## Start previously stopped services
	@echo "$(CYAN)Starting services...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) start

ps:  ## Show running services
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) ps

# -------------------------------------------------------------------
# Logs
# -------------------------------------------------------------------

logs:  ## View logs from all services
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) logs -f

logs-back:  ## View backend logs only
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) logs -f backend

logs-front:  ## View frontend logs only
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) logs -f frontend

logs-db:  ## View PostgreSQL logs only
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) logs -f postgres

logs-redis:  ## View Redis logs only
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) logs -f redis

# -------------------------------------------------------------------
# Shell Access
# -------------------------------------------------------------------

shell:  ## Open bash shell in backend container
	@echo "$(CYAN)Opening shell in backend container...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend bash

shell-db:  ## Open PostgreSQL shell (psql)
	@echo "$(CYAN)Opening PostgreSQL shell...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec postgres psql -U edulite_user -d edulite

shell-redis:  ## Open Redis CLI
	@echo "$(CYAN)Opening Redis CLI...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec redis redis-cli

shell-front:  ## Open shell in frontend container
	@echo "$(CYAN)Opening shell in frontend container...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec frontend sh

# -------------------------------------------------------------------
# Django Management
# -------------------------------------------------------------------

migrate:  ## Run Django database migrations
	@echo "$(CYAN)Running Django migrations...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend python manage.py migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

makemigrations:  ## Create new Django migrations
	@echo "$(CYAN)Creating new migrations...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend python manage.py makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

createsuperuser:  ## Create Django superuser
	@echo "$(CYAN)Creating Django superuser...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend python manage.py createsuperuser

collectstatic:  ## Collect static files
	@echo "$(CYAN)Collecting static files...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend python manage.py collectstatic --noinput
	@echo "$(GREEN)✓ Static files collected$(NC)"

# -------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------

test:  ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec backend python manage.py test

test-front:  ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) exec frontend npm test

# -------------------------------------------------------------------
# Build & Cleanup
# -------------------------------------------------------------------

build:  ## Build all Docker images
	@echo "$(CYAN)Building Docker images...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) build

rebuild:  ## Rebuild all images from scratch (no cache)
	@echo "$(CYAN)Rebuilding all images from scratch...$(NC)"
	cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Images rebuilt$(NC)"

clean:  ## Stop and remove containers, networks, volumes (WARNING: Deletes data!)
	@echo "$(RED)⚠️  WARNING: This will delete ALL containers, networks, and volumes!$(NC)"
	@echo "$(RED)This includes your database, media files, and Redis data.$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) down -v; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Aborted$(NC)"; \
	fi

# -------------------------------------------------------------------
# Quick Actions
# -------------------------------------------------------------------

quickstart:  ## Quick start - build and run everything
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(CYAN)  EduLite Quick Start$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@if [ ! -f $(DOCKER_DIR)/.env ]; then \
		echo "$(YELLOW)Creating .env file from .env.example...$(NC)"; \
		cp $(DOCKER_DIR)/.env.example $(DOCKER_DIR)/.env; \
		echo "$(GREEN)✓ .env file created$(NC)"; \
		echo "$(YELLOW)⚠️  Please edit $(DOCKER_DIR)/.env and update secrets!$(NC)"; \
		echo ""; \
	fi
	@echo "$(CYAN)Building images...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) build
	@echo ""
	@echo "$(CYAN)Starting services...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  EduLite is ready!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Access your application:$(NC)"
	@echo "  Frontend:  $(GREEN)http://localhost:5173$(NC)"
	@echo "  Backend:   $(GREEN)http://localhost:8000$(NC)"
	@echo "  API Docs: $(GREEN)http://localhost:8000/redoc/$(NC)"
	@echo "  API Swagger: $(GREEN)http://localhost:8000/swagger/$(NC)"
	@echo ""
	@echo "$(CYAN)Useful commands:$(NC)"
	@echo "  make logs          - View logs"
	@echo "  make shell         - Backend shell"
	@echo "  make help          - See all commands"
	@echo ""

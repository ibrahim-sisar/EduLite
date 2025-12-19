#!/bin/bash
# ===================================================================
# EduLite Backend Entrypoint Script
# ===================================================================
# This script runs before starting the Django/Daphne server.
# It waits for dependencies and performs initialization tasks.
# ===================================================================

set -e  # Exit on error

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  EduLite Backend Starting...${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

# -------------------------------------------------------------------
# Wait for PostgreSQL
# -------------------------------------------------------------------
echo -e "${CYAN}🔍 Waiting for PostgreSQL...${NC}"

# Extract PostgreSQL host from DATABASE_URL (format: postgresql://user:pass@host:port/db)
POSTGRES_HOST=$(echo $DATABASE_URL | sed -E 's/.*@([^:]+):.*/\1/')

until pg_isready -h "${POSTGRES_HOST}" -U edulite_user > /dev/null 2>&1; do
  echo -e "${YELLOW}   PostgreSQL is unavailable - sleeping${NC}"
  sleep 1
done

echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# -------------------------------------------------------------------
# Wait for Redis
# -------------------------------------------------------------------
echo -e "${CYAN}🔍 Waiting for Redis...${NC}"

until redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping > /dev/null 2>&1; do
  echo -e "${YELLOW}   Redis is unavailable - sleeping${NC}"
  sleep 1
done

echo -e "${GREEN}✓ Redis is ready${NC}"
echo ""

# -------------------------------------------------------------------
# Run Database Migrations
# -------------------------------------------------------------------
echo -e "${CYAN}📦 Running database migrations...${NC}"

if python manage.py migrate --noinput; then
  echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
  echo -e "${RED}✗ Migration failed${NC}"
  exit 1
fi
echo ""

# -------------------------------------------------------------------
# Collect Static Files
# -------------------------------------------------------------------
echo -e "${CYAN}📁 Collecting static files...${NC}"

if python manage.py collectstatic --noinput --clear; then
  echo -e "${GREEN}✓ Static files collected${NC}"
else
  echo -e "${YELLOW}⚠ Static files collection failed (non-critical)${NC}"
fi
echo ""

# -------------------------------------------------------------------
# Display Startup Information
# -------------------------------------------------------------------
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Starting Daphne ASGI Server${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  HTTP/WebSocket: ${GREEN}0.0.0.0:8000${NC}"
echo -e "${CYAN}  Health Check:   ${GREEN}http://localhost:8000/api/health/${NC}"
echo -e "${CYAN}  Admin Panel:    ${GREEN}http://localhost:8000/admin/${NC}"
echo -e "${CYAN}  API Docs:       ${GREEN}http://localhost:8000/api/schema/swagger-ui/${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

# -------------------------------------------------------------------
# Execute CMD from Dockerfile
# -------------------------------------------------------------------
exec "$@"

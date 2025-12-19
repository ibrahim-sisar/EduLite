#!/bin/sh
# ===================================================================
# EduLite Frontend Entrypoint Script
# ===================================================================
# This script runs before starting the Vite dev server.
# It ensures dependencies are installed and ready.
# ===================================================================

set -e  # Exit on error

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "${CYAN}═══════════════════════════════════════════════════${NC}"
echo "${CYAN}  EduLite Frontend Starting...${NC}"
echo "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

# -------------------------------------------------------------------
# Install/Update Dependencies
# -------------------------------------------------------------------
echo "${CYAN}📦 Checking npm dependencies...${NC}"

# Check if node_modules exists and is not empty
if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules)" ]; then
  echo "${CYAN}Installing dependencies...${NC}"
  npm install
  echo "${GREEN}✓ Dependencies installed${NC}"
else
  # Check if package.json has been modified
  echo "${GREEN}✓ Dependencies already installed${NC}"
fi
echo ""

# -------------------------------------------------------------------
# Verify/Setup project_choices_data
# -------------------------------------------------------------------
echo "${CYAN}🔍 Setting up project_choices_data...${NC}"

# The package.json script tries to copy from ../../project_choices_data
# But in Docker, the data is already in public/. Create the source location
# to prevent the copy script from failing.
mkdir -p ../../project_choices_data
cp -r public/project_choices_data/* ../../project_choices_data/ 2>/dev/null || echo "${CYAN}Data already in place${NC}"

if [ -d "public/project_choices_data" ] && [ -n "$(ls -A public/project_choices_data 2>/dev/null)" ]; then
  echo "${GREEN}✓ project_choices_data ready${NC}"
else
  echo "${RED}✗ project_choices_data setup failed${NC}"
  exit 1
fi
echo ""

# -------------------------------------------------------------------
# Display Startup Information
# -------------------------------------------------------------------
echo "${CYAN}═══════════════════════════════════════════════════${NC}"
echo "${CYAN}  Starting Vite Dev Server${NC}"
echo "${CYAN}═══════════════════════════════════════════════════${NC}"
echo "${CYAN}  Local:    ${GREEN}http://localhost:5173${NC}"
echo "${CYAN}  Network:  ${GREEN}http://0.0.0.0:5173${NC}"
echo "${CYAN}  Hot reload enabled for instant updates${NC}"
echo "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

# -------------------------------------------------------------------
# Execute CMD from Dockerfile
# -------------------------------------------------------------------
exec "$@"

# ===================================================================
# EduLite Frontend Dockerfile - Multi-stage Node build
# ===================================================================
# Build context: / (repository root)
# This Dockerfile creates an optimized container for the React/Vite
# frontend with hot module replacement (HMR) for development.
# ===================================================================

# -------------------------------------------------------------------
# Stage 1: Base - Node environment
# -------------------------------------------------------------------
FROM node:20-alpine as base

# Set working directory
WORKDIR /app

# Set environment variables for better npm behavior
ENV NPM_CONFIG_LOGLEVEL=warn \
    NPM_CONFIG_UPDATE_NOTIFIER=false

# -------------------------------------------------------------------
# Stage 2: Dependencies - npm packages
# -------------------------------------------------------------------
FROM base as dependencies

# Copy package files for dependency installation
# (Separate layer for better Docker caching)
COPY Frontend/EduLiteFrontend/package.json Frontend/EduLiteFrontend/package-lock.json ./

# Install dependencies using npm ci for reproducible builds
RUN npm ci --prefer-offline --no-audit

# -------------------------------------------------------------------
# Stage 3: Runtime - Application code
# -------------------------------------------------------------------
FROM dependencies as runtime

# Copy application source code from Frontend/EduLiteFrontend
COPY Frontend/EduLiteFrontend/ /app/

# CRITICAL: Copy project_choices_data from repository root
COPY project_choices_data ./public/project_choices_data

# Note: entrypoint.sh will be bind-mounted via docker-compose.yml

# Expose Vite dev server port
EXPOSE 5173

# Set entrypoint and default command
# Note: entrypoint.sh is mounted via volume in docker-compose.yml
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

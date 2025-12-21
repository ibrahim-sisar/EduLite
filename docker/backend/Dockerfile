# ===================================================================
# EduLite Backend Dockerfile - Multi-stage Python build
# ===================================================================
# Build context: /backend (parent of EduLite/)
# This Dockerfile creates an optimized container for the Django backend
# with Daphne ASGI server for HTTP and WebSocket support.
# ===================================================================

# -------------------------------------------------------------------
# Stage 1: Base - System dependencies
# -------------------------------------------------------------------
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# - postgresql-client: for pg_isready health checks and database management
# - curl: for health checks
# - build-essential: for compiling Python packages (psycopg2)
# - redis-tools: for redis-cli health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    build-essential \
    libpq-dev \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# -------------------------------------------------------------------
# Stage 2: Dependencies - Python packages
# -------------------------------------------------------------------
FROM base as dependencies

# Copy requirements.txt from backend directory (build context is now repo root)
COPY backend/requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# -------------------------------------------------------------------
# Stage 3: Runtime - Application code
# -------------------------------------------------------------------
FROM dependencies as runtime

# Copy Django project from backend/EduLite/ subdirectory
COPY backend/EduLite/ /app/

# Copy project choices data to container root for production deployments
# (Development uses volume mount from docker-compose.yml)
COPY project_choices_data/ /project_choices_data/

# Note: entrypoint.sh will be bind-mounted via docker-compose.yml
# This allows for easy editing without rebuilding the image

# Create directories for logs, media, and static files
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chmod 755 /app/logs /app/media /app/staticfiles

# Expose port 8000 for Daphne ASGI server
EXPOSE 8000

# Set entrypoint and default command
# Note: entrypoint.sh is mounted via volume in docker-compose.yml
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "EduLite.asgi:application"]

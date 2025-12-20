# 🐋 EduLite Docker Development Environment

Complete Docker setup for running EduLite locally with all services (backend, frontend, database, and Redis).

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)
- 4GB RAM minimum
- 10GB free disk space

### First Time Setup

```bash
# 1. Navigate to docker directory
cd docker/

# 2. Create environment file
cp .env.example .env

# 3. (Optional) Edit .env and update secrets
nano .env

# 4. Start everything!
make quickstart

# OR manually:
docker compose build
docker compose up -d
```

### Access Your Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/schema/swagger-ui/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📋 Available Commands

We've provided a Makefile with convenient commands. Run `make help` to see all options.

### Essential Commands

```bash
make dev          # Start all services (foreground with logs)
make up           # Start all services (background)
make down         # Stop all services
make logs         # View logs from all services
make shell        # Open shell in backend container
make migrate      # Run database migrations
make test         # Run backend tests
```

### Development Workflow

```bash
# Start development environment
make up

# View logs
make logs-back    # Backend only
make logs-front   # Frontend only

# Run migrations after model changes
make makemigrations
make migrate

# Create admin user
make createsuperuser

# Run tests
make test         # Backend tests
make test-front   # Frontend tests

# Access database
make shell-db     # PostgreSQL shell
make shell-redis  # Redis CLI

# Stop everything
make down
```

### Database Management

```bash
# Backup database
make db-backup

# Restore from backup
make db-restore FILE=backups/edulite_backup_20231219_120000.sql

# Reset database (⚠️ DELETES ALL DATA!)
make db-reset
```

### Cleanup

```bash
# Stop and remove containers (preserves data)
make down

# Remove everything including volumes (⚠️ DELETES ALL DATA!)
make clean

# Complete rebuild
make rebuild
```

---

## 🏗️ Architecture

### Services

| Service | Description | Port | Image |
|---------|-------------|------|-------|
| **backend** | Django + Daphne ASGI server | 8000 | Custom (Python 3.12) |
| **frontend** | React + Vite dev server | 5173 | Custom (Node 20) |
| **postgres** | PostgreSQL database | 5432 | postgres:16-alpine |
| **redis** | Redis for WebSocket channels | 6379 | redis:7-alpine |

### Data Persistence

Named volumes ensure your data persists across container restarts:

- `postgres_data` - Database tables and content
- `redis_data` - Channel layer state
- `media_data` - User uploads (profile pics, notes)
- `static_data` - Collected static files
- `logs_data` - Application logs

---

## ⚙️ Configuration

### Environment Variables

The main `.env` file in this directory controls Docker Compose variables.

**Required Variables:**

```env
POSTGRES_PASSWORD=your_secure_password_here
DJANGO_SECRET_KEY=your_secret_key_here
```

**Generating Secrets:**

```bash
# Generate PostgreSQL password
openssl rand -base64 32

# Generate Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Frontend Configuration

Frontend environment variables are set in `docker-compose.yml`:

- `VITE_API_BASE_URL` - Backend API endpoint
- `VITE_WS_BASE_URL` - WebSocket endpoint

### Backend Configuration

Backend reads environment variables from Docker Compose:

- `DATABASE_URL` - PostgreSQL connection string (auto-configured)
- `REDIS_HOST` / `REDIS_PORT` - Redis connection (auto-configured)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

---

## 🔧 Customization

### Docker Compose Override

Create `docker-compose.override.yml` for personal customizations that won't be committed:

```yaml
version: '3.8'

services:
  backend:
    # Add custom environment variables
    environment:
      - CUSTOM_VAR=value
    # Change ports
    ports:
      - "8080:8000"

  frontend:
    # Mount additional directories
    volumes:
      - ./custom-data:/app/custom
```

### Port Conflicts

If default ports are already in use, edit `docker-compose.yml` or create an override file:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Use 8080 instead of 8000
  frontend:
    ports:
      - "3000:5173"  # Use 3000 instead of 5173
```

---

## 🐛 Troubleshooting

### Common Issues

#### Services won't start

```bash
# Check service status
docker compose ps

# View logs for errors
make logs

# Try rebuilding
make rebuild
```

#### Database connection errors

```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U edulite_user

# View database logs
make logs-db

# Reset database (⚠️ deletes data!)
make db-reset
```

#### Port already in use

```bash
# Check what's using the port
sudo lsof -i :8000  # Backend
sudo lsof -i :5173  # Frontend
sudo lsof -i :5432  # PostgreSQL

# Stop conflicting service or change ports (see Customization)
```

#### Frontend can't connect to backend

```bash
# Verify backend is running
curl http://localhost:8000/api/health/

# Check CORS settings in docker-compose.yml
# Ensure CORS_ALLOWED_ORIGINS includes frontend URL
```

#### "permission denied" errors

```bash
# On Linux, you may need to fix file permissions
sudo chown -R $USER:$USER ../backend/EduLite/media
sudo chown -R $USER:$USER ../backend/EduLite/logs

# Or run Docker as your user (add yourself to docker group)
sudo usermod -aG docker $USER
# Then log out and back in
```

#### Hot reload not working

```bash
# For backend: Check file is mounted
docker compose exec backend ls -la /app

# For frontend: Vite may need polling on some systems
# Edit docker-compose.yml, add to frontend environment:
# CHOKIDAR_USEPOLLING=true
```

### Complete Reset

If everything is broken, nuclear option:

```bash
# Stop and remove everything
make clean

# Remove all Docker resources (⚠️ affects ALL Docker projects!)
make prune

# Rebuild from scratch
make quickstart
```

---

## 📖 Development Tips

### Hot Reload

Both backend and frontend support hot reload:

- **Backend**: Code changes automatically reload Django/Daphne
- **Frontend**: Vite HMR updates instantly in browser

### Database Access

Multiple ways to access PostgreSQL:

```bash
# 1. Via make command
make shell-db

# 2. Via Docker directly
docker compose exec postgres psql -U edulite_user -d edulite

# 3. Via external tool (pgAdmin, DataGrip, etc.)
# Host: localhost
# Port: 5432
# Database: edulite
# User: edulite_user
# Password: (from .env file)
```

### Running Django Management Commands

```bash
# Via make
make migrate
make makemigrations
make createsuperuser

# Via shell
make shell
python manage.py <command>

# Direct execution
docker compose exec backend python manage.py <command>
```

### Debugging

```bash
# View all logs
make logs

# Follow backend logs only
make logs-back

# View last 100 lines
docker compose logs --tail=100 backend

# Filter logs by service
docker compose logs backend | grep ERROR
```

### Performance

```bash
# Check resource usage
docker stats

# Check container health
make health

# Clean up unused resources
docker system df  # Show disk usage
make prune        # Clean up
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
make test

# Run specific app tests
docker compose exec backend python manage.py test users

# Run with coverage
make test-coverage

# Run specific test class
docker compose exec backend python manage.py test users.tests.UserTests
```

### Frontend Tests

```bash
# Run all tests
make test-front

# Run in watch mode
docker compose exec frontend npm run test:watch

# Run with coverage
docker compose exec frontend npm run test:coverage
```

---

## 📦 Production Considerations

This Docker setup is optimized for **development**. For production deployment:

1. **Don't use this directly** - Use proper production Docker images
2. **Security**:
   - Change all default passwords
   - Set `DEBUG=False` in Django
   - Use proper secrets management
   - Enable HTTPS
3. **Performance**:
   - Use Gunicorn/uWSGI instead of Daphne for HTTP
   - Keep Daphne for WebSocket
   - Use nginx reverse proxy
   - Enable caching
4. **Database**:
   - Use managed database service or dedicated PostgreSQL server
   - Regular backups
   - Connection pooling
5. **Monitoring**:
   - Add logging aggregation
   - Health check endpoints
   - Metrics collection

See `/deploy/` directory for production Ansible deployment.

---

## 🆘 Getting Help

- **Documentation**: Check `/Documentation/` directory
- **Issues**: Open an issue on GitHub
- **Discord**: Join our community server
- **Contributing**: See `/CONTRIBUTING.md`

---

## 📝 File Structure Reference

```
docker/
├── docker-compose.yml              # Main orchestration file
├── docker-compose.override.yml     # Personal customizations (gitignored)
├── .env                            # Secrets and config (gitignored)
├── .env.example                    # Template for .env
├── .gitignore                      # Ignore sensitive files
├── Makefile                        # Convenience commands
├── README.md                       # This file
├── backend/
│   ├── Dockerfile                  # Backend image definition
│   └── entrypoint.sh               # Backend startup script
└── frontend/
    ├── Dockerfile                  # Frontend image definition
    └── entrypoint.sh               # Frontend startup script
```

---

**Happy coding! 🚀**

If you encounter any issues not covered here, please open an issue or ask in Discord.

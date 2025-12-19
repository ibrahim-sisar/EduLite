---
name: General Issue Report
about: Describe a problem or suggest an improvement
title: "[INFRA] Complete Docker Development Environment Rewrite"
labels: 'infrastructure, docker, enhancement, good first issue'
assignees: ''

---

## Claiming This Task:

Please read the [Git Workflow Wiki Page](https://github.com/ibrahim-sisar/EduLite/wiki/Development-Git-Workflow) for updated community documentation.

Before you start working, please check the **Assignees** section on the right. If no one is assigned, leave a comment claiming the issue and assign it to yourself. This is required to prevent duplicate work.

## **Current Situation**

The existing Docker setup in `Docker-Files/` has several limitations that make it difficult for new contributors to get started and doesn't match our production infrastructure needs:

**Problems with Current Setup:**
- ❌ No PostgreSQL service (uses SQLite only, causing production/dev parity issues)
- ❌ No Redis service (required for Django Channels WebSocket support)
- ❌ Complex single Dockerfile tries to handle both backend and frontend
- ❌ 135-line entrypoint script with manual venv management
- ❌ No database migrations run automatically
- ❌ No health checks for services
- ❌ Inconsistent with our modern deployment architecture (Storm Cloud uses Ansible + Docker Compose)
- ❌ 153-line README that's overwhelming for beginners
- ❌ Complex UID/GID handling that confuses new contributors

**Why This Matters:**
- New contributors spend hours debugging Docker setup instead of contributing code
- Database inconsistencies between dev (SQLite) and prod (PostgreSQL) cause bugs
- WebSocket chat features don't work without Redis running separately
- No clear path from development to production deployment

## **Proposed Solution(s)

Create a new, modern Docker Compose setup in `/docker/` that provides a complete development environment with production parity:

### Architecture (4 Services):

```yaml
services:
  backend:     # Django + Daphne ASGI server (HTTP + WebSocket)
  frontend:    # React 19 + Vite dev server  
  postgres:    # PostgreSQL 16 database
  redis:       # Redis 7 (for Django Channels layer)
```

### Key Improvements:

1. **Service Separation**
   - Dedicated Dockerfile for backend (`docker/backend/Dockerfile`)
   - Dedicated Dockerfile for frontend (`docker/frontend/Dockerfile`)
   - Focused, maintainable entrypoint scripts

2. **PostgreSQL from Day 1**
   - Production parity (same database in dev and prod)
   - Better concurrency and JSON field support
   - Automatic migrations on startup

3. **Redis Integration**
   - Required for real-time chat (Django Channels)
   - Persistence enabled (AOF mode)
   - No more "chat doesn't work" issues

4. **Developer Experience**
   - One command to start: `docker compose up`
   - Hot reload for both Python and React changes
   - Clear `.env.example` files for configuration
   - Makefile with convenience commands (`make dev`, `make logs`, `make shell`)

5. **Named Volumes for Persistence**
   - `postgres_data` - Database survives restarts
   - `media_data` - User uploads persist
   - `redis_data` - Channel layer state

6. **Environment Variable Strategy**
   - Backend reads from `backend/EduLite/.env`
   - Frontend reads from `Frontend/EduLiteFrontend/.env`
   - Template files: `docker/.env.example`

### File Structure:

```
/docker/                          # NEW - Clean, organized
├── docker-compose.yml            # Main orchestration
├── docker-compose.override.yml   # Local dev overrides (gitignored)
├── .env.example                  # Template with all required vars
├── backend/
│   ├── Dockerfile                # Python 3.12 multi-stage build
│   └── entrypoint.sh             # Migrations + Daphne startup
├── frontend/
│   ├── Dockerfile                # Node 20 build
│   └── entrypoint.sh             # npm install + dev server
├── Makefile                      # Convenience commands
└── README.md                     # Quick start guide

/Docker-Files/                    # OLD - TO BE DELETED
```

## **Benefits**

### For New Contributors:
✅ **5-minute setup** instead of hours of debugging  
✅ **Just works™** - All services configured correctly out of the box  
✅ **Clear documentation** - Step-by-step quick start guide  
✅ **No manual Redis/PostgreSQL installation** - Everything in Docker

### For Existing Contributors:
✅ **Production parity** - Same database in dev and prod prevents bugs  
✅ **Hot reload** - See code changes instantly without rebuilding  
✅ **Easy cleanup** - `docker compose down -v` resets everything  
✅ **Debugging tools** - Direct access to database, Redis, and logs

### For the Project:
✅ **Reduced onboarding friction** - More contributors can start faster  
✅ **Fewer "it works on my machine" bugs** - Consistent environment  
✅ **Foundation for CI/CD** - Basis for automated testing pipeline  
✅ **Scalable architecture** - Easy to add services (Celery, nginx, etc.)

### For Code Quality:
✅ **Better testing** - Can test WebSocket features locally  
✅ **Realistic data** - PostgreSQL matches production behavior  
✅ **Integration testing** - All services running together

## **Files to be Altered or Created**

### New Files to Create:

```
docker/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── Dockerfile
│   └── entrypoint.sh
├── Makefile
└── README.md
```

### Files to Update:

```
backend/requirements.txt
  - Add: psycopg2-binary (PostgreSQL driver)
  - Add: dj-database-url (for DATABASE_URL parsing)

backend/EduLite/EduLite/settings.py
  - Update DATABASES to read from DATABASE_URL env var
  - Update CHANNEL_LAYERS to read REDIS_HOST from env
  - Update ALLOWED_HOSTS to read from env
  - Update CORS_ALLOWED_ORIGINS to read from env

backend/EduLite/.env.example (NEW)
  - Template for backend environment variables

Frontend/EduLiteFrontend/.env.example (UPDATE)
  - Add VITE_WS_BASE_URL for WebSocket connection

README.md (ROOT)
  - Update "Getting Started" section
  - Point to new docker/ directory
  - Remove references to Docker-Files/

CONTRIBUTING.md
  - Update Docker setup instructions
  - Add troubleshooting section

.gitignore
  - Add docker-compose.override.yml
  - Add backend/EduLite/.env
```

### Files/Directories to Delete:

```
Docker-Files/                     # Entire directory
Documentation/DOCKER-README.md    # Outdated (archive if needed)
```

## **Implementation Checklist**

### Phase 1: Docker Infrastructure
- [ ] Create `docker/` directory structure
- [ ] Write `docker/backend/Dockerfile` with multi-stage build
- [ ] Write `docker/frontend/Dockerfile` with multi-stage build
- [ ] Write `docker/backend/entrypoint.sh` (migrations + Daphne)
- [ ] Write `docker/frontend/entrypoint.sh` (npm install + dev)
- [ ] Write `docker/docker-compose.yml` with all 4 services
- [ ] Write `docker/.env.example` with documentation
- [ ] Write `docker/Makefile` with convenience commands
- [ ] Write `docker/README.md` with quick start guide

### Phase 2: Backend Configuration
- [ ] Add `psycopg2-binary>=2.9.9` to `backend/requirements.txt`
- [ ] Add `dj-database-url>=2.1.0` to `backend/requirements.txt`
- [ ] Update `settings.py` to read `DATABASE_URL` from environment
- [ ] Update `settings.py` to read `REDIS_HOST` from environment
- [ ] Update `settings.py` to read `ALLOWED_HOSTS` from environment
- [ ] Update `settings.py` to read `CORS_ALLOWED_ORIGINS` from environment
- [ ] Create `backend/EduLite/.env.example` template
- [ ] Add health check endpoint at `/api/health/`

### Phase 3: Frontend Configuration
- [ ] Update `Frontend/EduLiteFrontend/.env.example` with WebSocket URL
- [ ] Ensure WebSocket client reads WS URL from env var (if hardcoded)

### Phase 4: Documentation
- [ ] Update root `README.md` with new Docker instructions
- [ ] Update `CONTRIBUTING.md` with Docker setup steps
- [ ] Update `Documentation/CONTRIBUTING.md` if separate
- [ ] Add troubleshooting section to `docker/README.md`

### Phase 5: Cleanup
- [ ] Delete `Docker-Files/` directory entirely
- [ ] Archive `Documentation/DOCKER-README.md` if needed
- [ ] Update `.gitignore` with new Docker-related entries

### Phase 6: Testing
- [ ] Test: `docker compose up` starts all services cleanly
- [ ] Test: Backend accessible at http://localhost:8000
- [ ] Test: Frontend accessible at http://localhost:5173
- [ ] Test: PostgreSQL connection works (run migrations)
- [ ] Test: Redis connection works (WebSocket chat)
- [ ] Test: Hot reload works for Python file changes
- [ ] Test: Hot reload works for React file changes
- [ ] Test: Media uploads persist across container restarts
- [ ] Test: Database data persists across container restarts
- [ ] Test: WebSocket connections establish successfully
- [ ] Test: Chat messages deliver in real-time
- [ ] Test: `make dev`, `make logs`, `make shell` commands work
- [ ] Test: `docker compose down -v` cleans up properly
- [ ] Test: Fresh setup from scratch (delete volumes, rebuild)

## **Additional Context (Optional)**

### Technical Specifications:

**Backend Container:**
- Base: `python:3.12-slim`
- Port: 8000 (HTTP + WebSocket via Daphne ASGI)
- Health check: `curl -f http://localhost:8000/api/health/ || exit 1`
- Volumes: Code mount + named volumes for media and logs

**Frontend Container:**
- Base: `node:20-alpine`
- Port: 5173
- Command: `npm run dev -- --host 0.0.0.0`
- Volumes: Code mount + anonymous volume for node_modules

**PostgreSQL Container:**
- Base: `postgres:16-alpine`
- Port: 5432 (exposed for debugging)
- Health check: `pg_isready -U edulite_user`
- Volume: `postgres_data:/var/lib/postgresql/data`

**Redis Container:**
- Base: `redis:7-alpine`
- Port: 6379 (exposed for debugging)
- Command: `redis-server --appendonly yes`
- Health check: `redis-cli ping`
- Volume: `redis_data:/data`

### Environment Variables Reference:

**Backend (.env):**
```env
DJANGO_SECRET_KEY=<generate-with-openssl-rand-base64-32>
DEBUG=True
DATABASE_URL=postgresql://edulite_user:edulite_pass@postgres:5432/edulite
REDIS_HOST=redis
REDIS_PORT=6379
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_TOKEN_REFRESH_BUFFER=30
VITE_USE_SESSION_STORAGE=true
```

### Makefile Commands:

```makefile
make dev         # Start all services in foreground
make up          # Start all services in background
make down        # Stop all services
make restart     # Restart all services
make logs        # View logs from all services
make logs-back   # View backend logs only
make logs-front  # View frontend logs only
make shell       # Open shell in backend container
make migrate     # Run Django migrations
make makemigrations  # Generate new migrations
make createsuperuser # Create Django admin user
make test        # Run backend tests
make test-front  # Run frontend tests
make clean       # Stop and remove all containers, networks, volumes
make rebuild     # Clean rebuild of all services
```

### Success Metrics:

This issue is complete when:
1. A new contributor can clone the repo and run `docker compose up` to get a fully working environment in under 5 minutes
2. All 4 services start cleanly with no manual intervention
3. Database migrations run automatically
4. WebSocket chat works immediately after startup
5. Code changes hot reload for both backend and frontend
6. Documentation clearly explains the setup process
7. Old `Docker-Files/` directory is deleted

### References:

- Django Channels Redis: https://channels.readthedocs.io/en/stable/topics/channel_layers.html
- Docker Compose Best Practices: https://docs.docker.com/compose/production/
- PostgreSQL Docker Image: https://hub.docker.com/_/postgres
- Redis Docker Image: https://hub.docker.com/_/redis
- Storm Cloud deployment (similar architecture): `/deploy/` folder in this repo

### Related Issues:

- Closes #??? (if there's an existing Docker issue)
- Related to future CI/CD implementation
- Foundation for automated testing infrastructure

---

**Priority:** High  
**Effort:** Medium (8-12 hours for complete implementation)  
**Skills Needed:** Docker, Docker Compose, Django, React, PostgreSQL, Redis  
**Good for:** Contributors with DevOps experience or those wanting to learn Docker

**Questions?** Ask in the Discord #infrastructure channel or comment on this issue!

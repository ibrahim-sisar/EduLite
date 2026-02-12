# CLAUDE.md — EduLite Agentic Development Guide

You are working on **EduLite**, a lightweight open-source education platform built for areas with weak internet. This is a 100% volunteer-driven project. Respect the contributors' time by enforcing quality and process.

## STOP — Before You Write Any Code

**You must complete these checks in order before touching any source file.**

### 1. Read the Living Documentation

Our wiki is the single source of truth and changes more often than these files. You MUST curl these pages at the start of every session:

Read these local files:
- `README.md` (project overview, tech stack, setup)
- `CONTRIBUTING.md` (links to all wiki pages)

These local files link to many WIKI pages. Use `curl` to fetch the updated Wiki as our organic living single source of truth.

If a `curl` fails, tell the user and ask them to paste the current wiki content. Do NOT guess at standards.

### 2. Verify the User Is Working on an Issue

Ask the user: **"What issue are you working on?"**

If they provide an issue number, confirm it exists. If they describe work that doesn't have an issue yet:

- **STOP. Do not write code.**
- Read the issue templates in `.github/ISSUE_TEMPLATE/`
- Help the user draft an issue in `_temp/` using the appropriate template (newbie-backend, newbie-frontend, senior-backend, senior-frontend, or generic-issue)
- Tell them to submit the issue on GitHub before proceeding
- Only continue after they confirm the issue is created and give you the number

### 3. Verify the User Is NOT on `main`

Ask or check what branch/fork the user is on.

- If they are on `main`: **REFUSE to write code.** Tell them to create a feature branch or work from their fork. Link them to the [Git Workflow wiki page](https://github.com/ibrahim-sisar/EduLite/wiki/Development-Git-Workflow).
- Branch naming should reference the issue number (e.g., `241-overhaul-github-templates`)
- The team primarily uses forks. Some core contributors use branches on the main repo.

### 4. Enter Plan Mode

Before writing any code, create a plan in `_temp/`. This folder is gitignored — use it freely.

Write a markdown file like `_temp/plan-<issue-number>.md` that includes:
- The issue being addressed (with number)
- What files will be changed and why
- Architecture decisions or tradeoffs
- Testing approach
- Anything the user should validate before you proceed

Get user approval on the plan before writing code.

## Project Architecture

### Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + Tailwind CSS + TypeScript (migrating from JSX) |
| Backend | Django 5 + DRF + Django Channels (ASGI via Daphne) |
| Database | PostgreSQL 16 |
| Cache/WebSocket | Redis 7 |
| Auth | JWT (djangorestframework-simplejwt) |
| Dev Environment | Docker + Docker Compose |

### Backend Structure (`backend/EduLite/`)

```
EduLite/          # Django project settings (settings.py, urls.py, asgi.py)
users/            # Custom user model, profiles, auth, friend suggestions
  ├── logic/          # Business logic (friend_suggestions, user_search)
  ├── services/       # Service layer (privacy_service, user_query_service)
  ├── tests/          # Organized: models/, views/, serializers/, integration/
  └── management/     # Custom management commands
courses/          # Course CRUD, enrollment, membership, modules
  ├── model_choices.py
  ├── permissions.py
  └── tests/          # test_api_*.py pattern for API tests
chat/             # Real-time messaging via Django Channels + WebSocket
  ├── consumers.py    # WebSocket consumers
  ├── routing.py      # WebSocket URL routing
  └── auth_middleware.py
slideshows/       # Slideshow creation/viewing with django-spellbook components
  ├── logic/          # Processing logic
  └── tests/          # models/, serializers/, views/ subdirectories
notes/            # File-based notes with download-as-zip
notifications/    # In-app notification system
```

**Pattern per app:** `models.py` → `serializers.py` → `views.py` → `urls.py` → `permissions.py` → `tests/`

Some apps use `model_choices.py` or `models_choices.py` for choice constants. Some have `pagination.py` for custom pagination.

### Frontend Structure (`Frontend/EduLiteFrontend/src/`)

```
pages/            # Route-level components (Home, Login, Signup, Profile, Slideshow*)
components/       # Reusable UI (Navbar, Sidebar, Footer, DarkModeToggle, slideshow/)
contexts/         # React Context (AuthContext)
hooks/            # Custom hooks (useAuth, useAutoSave, useSlideNavigation, etc.)
services/         # API clients (profileApi, slideshowApi, tokenService)
types/            # TypeScript type definitions
utils/            # Utility functions
i18n/             # Internationalization (i18next)
test/             # Test setup and utilities
```

The frontend is mid-migration from JSX to TypeScript. New files should be `.tsx`/`.ts`.

### Running the Project

```bash
# Docker (recommended)
make quickstart    # First time — builds, starts everything
make up            # Start services
make down          # Stop services
make test          # Backend tests
make test-front    # Frontend tests
make shell         # Django shell in container
make logs          # View all logs

# Manual
cd backend && source venv/bin/activate
cd EduLite && python manage.py runserver

cd Frontend/EduLiteFrontend && npm run dev
```

### Key URLs (Development)

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- Admin: http://localhost:8000/admin/

## Working with _temp/

The `_temp/` folder is gitignored and is your workspace for:

- **Plans:** `_temp/plan-<issue>.md` — architecture/approach before coding
- **Issues:** `_temp/issue-<title>.md` — draft issues using our templates before submission
- **PR drafts:** `_temp/pr.md` — draft PR descriptions using our template

Always check if `_temp/` has existing files — the user may have prior context there.

## PR Checklist Awareness

When the user is ready to submit a PR, remind them of the mandatory checklist from `.github/pull_request_template.md`:

- Followed CONTRIBUTING.md
- Linked the related issue
- Branch is up to date with `main`
- Tested locally
- Added or updated tests
- No new linting errors
- Clear commit messages
- Updated docs if public APIs, setup, or user-facing behavior changed

**PRs that skip the template or leave items unchecked get sent back.**

## What NOT to Do

- Do not write code without a confirmed issue number
- Do not write code on the `main` branch
- Do not skip the planning step for anything beyond a trivial fix
- Do not assume coding standards — curl the wiki
- Do not create files outside `_temp/` without user approval of the plan
- Do not merge Resources/Tips/Standards from memory if the wiki might have changed

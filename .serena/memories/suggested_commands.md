# EduLite Development Commands

## Backend Commands

### Setup and Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### Django Management
```bash
cd backend/EduLite

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Open Django shell
python manage.py shell
```

### Testing
```bash
cd backend/EduLite

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test courses
python manage.py test chat

# Run specific test file
python manage.py test users.tests.test_userregistration

# Run with verbosity
python manage.py test --verbosity=2

# Use Mercury for interactive test selection (recommended)
python -m mercury
```

### Code Quality
```bash
# Format code with Black (from project root)
black backend/

# Run type checking with mypy (manual, non-blocking)
mypy backend/EduLite

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Database
```bash
cd backend/EduLite

# Reset database (careful!)
python manage.py flush

# Create dummy users for testing
python manage.py create_dummy_users 10
python manage.py create_dummy_users 25 --password mynewpass
```

## Frontend Commands

### Setup and Installation
```bash
cd Frontend/EduLiteFrontend
npm install
```

### Development
```bash
cd Frontend/EduLiteFrontend

# Run development server (copies choice data automatically)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing
```bash
cd Frontend/EduLiteFrontend

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Code Quality
```bash
cd Frontend/EduLiteFrontend

# Run ESLint
npm run lint

# Type check TypeScript
npm run type-check
```

## Redis Server (Required for Chat)

### Start Redis
```bash
# On Ubuntu/Debian
sudo systemctl start redis-server

# On macOS (with Homebrew)
brew services start redis

# Using Docker
docker run -p 6379:6379 -d redis:latest
```

### Verify Redis
```bash
redis-cli
# Should open Redis CLI
```

## Docker Commands

```bash
# From Docker-Files directory
cd Docker-Files

# Build and start containers
./containers.sh

# Or use docker-compose directly
docker-compose up -d
docker-compose down
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Stage changes
git add .

# Commit (triggers pre-commit hooks)
git commit -m "feat: your commit message"

# Push to your branch
git push origin feature/your-feature-name

# Create PR on GitHub
```

## Useful Shortcuts

### Check if Django is working
```bash
cd backend/EduLite && python manage.py check
```

### Check if Redis is running
```bash
redis-cli ping
# Should respond with: PONG
```

### View all Django URLs
```bash
cd backend/EduLite && python manage.py show_urls
```

### Generate API schema
```bash
cd backend/EduLite && python manage.py spectacular --file schema.yml
```

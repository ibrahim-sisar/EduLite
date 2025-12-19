# EduLite Project Overview

## Purpose
EduLite is a **100% volunteer-driven open-source educational platform** designed for students in areas with weak internet connectivity. It was created during the COVID-19 pandemic and Gaza conflict to provide a student-first learning platform that works reliably in challenging conditions.

## Core Mission
- Lightweight, offline-capable education platform
- Works with poor connectivity
- Clean, age-friendly UI
- Real-time messaging between students and teachers
- Assignment/exam creation and submission
- Smart anti-cheating system
- Lecture scheduling and calendar integration

## Project Status
🚧 In active development - Currently building MVP features

## Tech Stack

### Backend
- **Python 3.10+** with **Django 5.2.1**
- **Django REST Framework 3.16.0** for APIs
- **Django Channels 4.2.2** for WebSocket support (real-time chat)
- **Redis** for Channels layer and caching
- **PostgreSQL** (production) / **SQLite** (development)
- **JWT** authentication (djangorestframework_simplejwt 5.5.0)
- **drf-spectacular** for OpenAPI/Swagger docs

### Frontend
- **React 19** with **TypeScript**
- **Vite** for build tooling
- **Tailwind CSS v4** for styling
- **React Router v7** for routing
- **i18next** for internationalization (supports Arabic and English)
- **Axios** for API requests

### Development Tools
- **Black** for Python code formatting
- **mypy** for type checking (optional, warning-only)
- **ESLint** for JavaScript/TypeScript linting
- **pre-commit** hooks for code quality
- **Mercury** for Django test management
- **Vitest** for frontend testing

## Project Structure

```
EduLite/
├── backend/
│   └── EduLite/
│       ├── EduLite/          # Django project settings
│       ├── users/            # User management, profiles, friends
│       ├── courses/          # Courses, modules, memberships
│       ├── chat/             # Real-time messaging (WebSocket)
│       ├── notifications/    # Notification system
│       └── notes/            # Note sharing and management
├── Frontend/
│   └── EduLiteFrontend/
│       └── src/
│           ├── components/   # React components
│           ├── pages/        # Page components
│           ├── services/     # API services
│           ├── contexts/     # React contexts (Auth, etc.)
│           ├── i18n/         # Internationalization
│           └── types/        # TypeScript type definitions
├── Docker-Files/             # Docker configuration
├── Documentation/            # API docs and guides
└── project_choices_data/     # JSON data for countries, languages, etc.
```

## Key Features Currently Implemented

### Users App
- User registration and authentication (JWT)
- User profiles with privacy settings
- Friend requests and friendships
- User search with privacy controls
- Profile privacy settings (search visibility, profile visibility, etc.)

### Courses App
- Course creation (teachers automatically enrolled)
- Course modules with GenericForeignKey for flexible content
- Course memberships (teacher, assistant, student roles)
- Course chatrooms (integration with chat app)
- Visibility controls (public, private, restricted)

### Chat App
- Real-time messaging via WebSockets
- Chat rooms
- Participant management
- Message history

### Notifications App
- Notification system for user events

### Notes App
- Note uploading and sharing
- Subject/level categorization

# 🎓 EduLite – The Lightweight Digital Education Platform

![EduLite](https://img.shields.io/badge/EduLite-Education%20for%20All-blue)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](https://github.com/ibrahim-sisar/EduLite/blob/main/CONTRIBUTING.md)
[![MIT License](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/ibrahim-sisar/EduLite/blob/main/LICENSE)
![Volunteer Project](https://img.shields.io/badge/Volunteer-Project-orange)
![No Funding](https://img.shields.io/badge/Open%20Source-No%20Funding-red)


> 🧡 **Note:** EduLite is a **100% volunteer-driven open source project**.
> There is **no funding or salaries** involved. Everyone contributes out of passion for learning and helping others.

## A student-first learning platform, built for areas with weak internet and real challenges.

---

## ✨ Vision

During the 2020 COVID-19 pandemic, I (the founder) was still young and found platforms like Microsoft Teams hard to use and slow. In 2023, a war broke out in Gaza and disconnected us from school for more than a year.

That’s when I asked:

> **“Why aren’t we building something made for students?”**

So I decided to build one — with you.

---

## 🚀 Features (Planned)

- ✅ Real-time messaging (Students ↔ Teachers)
- ✅ Assignment & exam creation and submission
- 🔒 Smart anti-cheating system
- 📅 Lecture scheduling & calendar integration
- 🎥 Google Meet integration
- 🧠 Clean, age-friendly UI
- ⚡ Extremely lightweight – works with poor connectivity

---

## 🏗️ Project Status: `🚧 In Development`

We are in the early planning phase. Currently working on:

- 📋 Gathering contributors
- 🧭 Writing full project vision
- ✏️ Creating UI wireframes (coming soon)
- 🧱 Starting backend models with Django
- 🌐 Initial frontend setup with React
- 🔜 Public demo (soon!)

---

## 🧑‍🤝‍🧑 Join the Team

We welcome **everyone** – beginner or expert!

### 👥 Roles Needed:

| Role | Description |
|------|-------------|
| 👨‍💻 Frontend Devs | React, HTML/CSS, Tailwind |
| 🧠 Backend Devs | Django, REST APIs |
| 🎨 UI/UX Designers | Help shape the look and feel |
| 🐞 Bug Testers | Find and report issues |
| 🧪 QA Engineers | Test before releases |
| 📷 Graphic Designers | Logos, icons, etc. |

👉 [Join via Google Form](https://forms.gle/JEvKtqbzcEJiVV7d6)
💬 Or [Chat with us on Discord](https://discord.gg/phXnxX2dD4)

---

## 🐋 Quick Start with Docker

The easiest way to get started is using Docker. We provide a complete development environment with all services pre-configured.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://www.gnu.org/software/make/) (usually pre-installed on Linux/Mac)

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/ibrahim-sisar/EduLite.git
   cd EduLite
   ```

2. **Quick start** (first time setup)
   ```bash
   make quickstart
   ```
   This will:
   - Create the `.env` file with auto-generated secrets
   - Build all Docker images
   - Start all services (backend, frontend, PostgreSQL, Redis)
   - Run database migrations
   - Collect static files

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/api/health/

### Useful Commands

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Backend shell (Django)
make shell

# Run migrations
make migrate

# Create superuser
make createsuperuser

# Run backend tests
make test

# Rebuild containers
make build

# Clean everything (including volumes)
make clean
```

For detailed Docker documentation, see [docker/README.md](docker/README.md).

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Django (Python) + DRF + Django Channels |
| Database | PostgreSQL 16 |
| Cache/WebSocket | Redis 7 |
| Auth | JWT (djangorestframework-simplejwt) |
| Deployment | Railway / Render / Vercel |
| Development | Docker + Docker Compose |
| Tools | Git, GitHub Projects, VSCode |

---

## 📌 What’s Next?

- [ ] Finalize UI wireframes
- [ ] Build MVP: Users, Courses, Messaging
- [ ] Release first working demo
- [ ] Collect early feedback

---

## 🤝 How to Contribute

1. Join a server or fill out a Google form
2. When I give you the authority to modify the repository, you create a new branch in your name.
3. Clone the repository to your machine and make sure you write to your branch.
4. **Set up your development environment:**
   - Using Docker (recommended): Run `make quickstart`
   - Manual setup: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions
5. Make your changes and test them
6. Commit your changes following our [coding standards](backend/CODING_STANDARDS.md)
7. Push & open a Pull Request
8. We'll review it together!

We're using **GitHub Projects** to track tasks.
Feel free to check our [Issues](https://github.com/ibrahim-sisar/EduLite/issues).

---

## 📜 License

MIT License – free to use, modify, and share.

---

## 👤 Made by

- **Ibrahim Abu Al-Roos** – Project Leader, backend dev
- **smattymatty** – backend developer
- **slaftamyr** – frontend developer
- **PacifistaPx0** - backend developer
> with ❤️ from *Palestine*, *Canada*, *Sudan*, *Nigeria* and the global open-source community.

---

## 🌍 Let’s Change Education Together

💥 Drop a “I’m in” on the [Discussions](https://github.com/ibrahim-sisar/EduLite/discussions),
📬 Or DM me on [GitHub](https://github.com/ibrahim-sisar).
💬 Or join discord server [EduLite](https://discord.gg/phXnxX2dD4)
📁 Or fill out a Google form [Forms](https://forms.gle/2LsCPrW44eHmTrwT8)

> 🌱 EduLite is for every student who just wants to learn — no matter where they are.

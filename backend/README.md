# 🧠 EduLite Backend

This is the backend part of EduLite – built with Django & Django REST Framework to serve APIs

## 🛠️ Tech Stack

- Python + Django  
- Django REST Framework  
- PostgreSQL / SQLite (for local dev)  
- Django JWT (for auth)

## 🗂️ Project Structure
```
backend/
├── EduLite/ # Django settings and project config
├── EduLite/media/ # Contains media for profile pictures
├── EduLite/users # App for managing users, includes registration
├── EduLite/chat # App for managing the lightweight chat system
├── project_choices_data/ # contains occupations.json, countries.json, etc.
├── README.md # backend documentation
└── manage.py
```

## ⚙️ Setup Redis Server

### Install on Ubuntu/Debian

```bash
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis
```

* Manually enable & start the redis server (In case if Redis doesn't start on reboot)
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Install on Red Hat/Rocky 

```bash
sudo yum install redis
```

* Manually enable & start the redis server (In case if Redis doesn't start on reboot)
```bash
sudo systemctl enable redis
sudo systemctl start redis
```

### Install on macOS

* Make sure you have [Homebrew](https://brew.sh/) installed
```bash
brew --version
```

* Install redis
```bash
brew install redis
```

* Start the redis process in background
```bash
brew services start redis
```

### Verify Redis Installation

* To test if redis server is running or not, execute `redis-cli`:
```bash
redis-cli
```

### Setup Redis Docker Container

* Make sure Docker is installed and running (Follow [this](https://docs.docker.com/engine/install/) document to setup docker on your machine)
```
docker --version
```

* Pull latest redis docker image
```
docker pull redis:latest
```

* Start a Redis container
```
docker run -p 6379:6379 -d redis:latest
```

* Verify the Redis container is running
```
docker ps
```

## 🚀 Getting Started

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Creating Dummy Users for Development

To populate your development database with sample users and profiles, use the `create_dummy_users` management command. This is helpful for testing UI components, APIs, and general development.

**How to Run:**

* To create 10 dummy users with the default password (`password123`):
    `python manage.py create_dummy_users 10`

* To create 25 dummy users with a custom password (e.g., `mynewpass`):
    `python manage.py create_dummy_users 25 --password mynewpass`

* For more options and help:
    `python manage.py create_dummy_users --help`

**Important Notes & TODOs:**

* **Development Use Only:** This command is intended for development and testing environments. Do not run it in production.
* **Default Password:** The default password for created users is `password123` unless overridden with the `--password` option. Ensure this is known by the development team.
* **Future Enhancements (TODO):** This command will be enhanced over time. Future versions may include arguments for:
    * Setting user status (e.g., `is_active`, email verification status).
    * Assigning users to specific groups.
    * Populating different profile types or more diverse profile data as new features are added to user profiles.

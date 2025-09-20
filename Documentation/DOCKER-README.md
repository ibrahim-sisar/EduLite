# EduLite Dockerized Development Environment

The directory (`Docker-Files/`) contains the necessary configurations to set up and run the EduLite project (both backend and frontend) in a consistent, isolated Docker environment using Docker Compose.

This setup is designed to simplify dependency management and provide a reproducible development experience.

## This is entirely optional, but recommended

If you're new to Docker, you might want to check out the [Docker Documentation](https://docs.docker.com/get-started/) to get started.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Docker Engine**: The core Docker runtime.
    * Installation guide: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
2.  **Docker Compose (v2 Plugin)**: The tool for defining and running multi-container Docker applications.
    * It's typically included with Docker Desktop. For Linux, it's often installed as a plugin to the Docker CLI (i.e., you use `docker compose` commands).
    * Installation guide: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
    * *This setup uses `docker compose` (with a space), not the older standalone `docker-compose` (with a hyphen).*

## Directory Contents

* `Dockerfile`: Defines the base image for both backend and frontend services. It installs:
  * Common development tools (Git, curl, nano, etc.)
  * Python 3, pip, and venv (for the Django backend)
  * Node.js (v20.x) and npm (for the React/Vite frontend)
  * Creates a non-root `user` for better volume mount permissions on Linux.
* `docker-compose.yml`: Defines the services for the application:
  * `backend`: Runs the Django application.
  * `frontend`: Runs the React/Vite development server.
  * Includes volume mounts to sync your local source code into the containers.
  * Configures port mappings.
* `containers.sh`: A helper script to manage the Docker Compose environment (build, up, down, shell, logs, etc.).
* `in-container-scripts/`: This directory (relative to the Dockerfile build context) contains helper scripts that are copied *into* the Docker image and used by the container or aliased for convenience:
  * `django_runserver.sh`: The entrypoint script for the `backend` service. It handles virtual environment setup, dependency installation, migrations, and starts the Django development server.

## Getting Started

1.  **Clone the EduLite Repository (if you haven't already):**
    ```bash
    git clone [https://github.com/ibrahim-sisar/EduLite.git](https://github.com/ibrahim-sisar/EduLite.git)
    cd EduLite
    ```

2.  **Navigate to this Directory:**
    ```bash
    cd Docker-Files
    ```
    *(Or ensure the `containers.sh` script, `Dockerfile`, and `docker-compose.yml` are in your current working directory when running commands, or adjust paths in the script if needed).*

3.  **Build the Docker Images:**
    The first time, or whenever you change the `Dockerfile` or need to rebuild with different build arguments, run:
    ```bash
    ./containers.sh build
    ```
    This command passes your current host UID and GID as build arguments to the `Dockerfile` to help with file permission issues on mounted volumes, especially for Linux users.

4.  **Start the Services:**
    To start the backend and frontend services in detached mode:
    ```bash
    ./containers.sh up
    ```
    * The backend Django server will be accessible on `http://localhost:8000` (or your host IP if not on localhost).
    * The frontend Vite development server will be accessible on `http://localhost:5173` (or your host IP).

## Using the Management Script (`containers.sh`)

This script simplifies common Docker Compose operations. All commands are run from the directory containing the script and `docker-compose.yml`.

* **Start all services:**
    ```bash
    ./containers.sh up
    ```
    (Add `--force-recreate` if you want to ensure containers are recreated, e.g., after a build or config change).

* **Stop all services (without removing containers):**
    ```bash
    ./containers.sh stop
    ```

* **Stop and remove containers, networks (volumes preserved by default):**
    ```bash
    ./containers.sh down
    ```

* **Stop and remove containers, networks, AND volumes (destructive full clean):**
    ```bash
    ./containers.sh clean
    ```
    *Use with caution, as this will delete any data stored in Docker volumes (like a development database if you add one).*

* **Rebuild images (e.g., after Dockerfile changes):**
    ```bash
    ./containers.sh build
    ```
    (Follow with `./containers.sh up --force-recreate` to use the new images).

* **Access a shell inside a service container (e.g., the backend):**
    ```bash
    ./containers.sh shell
    ```
    (This defaults to the `backend` service. To access another service, you might need to modify the script or use `docker compose exec <service_name> bash` directly).
    Inside the container, you'll see an intro message and can use aliases:

* **View logs from a service (e.g., the backend, follow mode):**
    ```bash
    ./containers.sh logs
    ```
    (Defaults to the `backend` service. Press `Ctrl+C` to stop following).
    To see logs for a specific service:
    ```bash
    ./containers.sh logs <service_name>
    ```

* **Check the status of services:**
    ```bash
    ./containers.sh status
    ```

* **Restart services:**
    ```bash
    ./containers.sh restart
    ```

* **View help for the script:**
    ```bash
    ./containers.sh help
    ```

## Project Structure (Inside Container - for reference)

* The Docker setup uses a non-root user named `user`.
* The working directory for this user is `/home/user`.
* **Backend Code**: Mounted from your host's `../backend` (relative to `docker-compose.yml`) to `/home/user/Edulite/backend` inside the container.
  * The Django project itself (containing `manage.py`) is expected to be in `/home/user/Edulite/backend/EduLite/`.
  * The Python virtual environment (`venv`) is created at `/home/user/Edulite/backend/venv/`.
* **Frontend Code**: Mounted from your host's `../Frontend/EduLiteFrontend` (relative to `docker-compose.yml`) to `/home/user/edulite/Frontend/EduLiteFrontend` inside the container.
  * The `working_dir` for the frontend service is set to this path.

## Entrypoint Script (`django_runserver.sh` for Backend)

When the `backend` service starts, the `/usr/local/bin/django_runserver.sh` script is executed as its main command. This script automatically:

1. Verifies the Django project structure.
2. Creates or ensures the Python virtual environment (`venv`) exists and is healthy.
3. Installs/updates Python dependencies from `requirements.txt` using the venv's `pip`.
4. Navigates to the Django project directory.
5. Runs Django database migrations (`python manage.py migrate`).
6. Starts the Django development server on `0.0.0.0:8000`.

---

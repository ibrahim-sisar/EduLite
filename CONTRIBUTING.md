# Contributing to EduLite 🎓

First off, thank you for considering contributing to EduLite! We're excited to build this student-first learning platform together. Your help is invaluable in making education accessible, especially in challenging environments.

This document provides guidelines for contributing to the project.


## Getting Started

### Prerequisites

Before you begin, please ensure you have the following installed:

- Git
- Python (version 3.8 or higher recommended)
- Node.js (LTS version recommended, which includes npm)
- pip (Python package installer)

### Forking & Cloning

1.  **Fork** the `ibrahim-sisar/EduLite` repository to your own GitHub account.
2.  **Clone** your fork to your local machine:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/EduLite.git](https://github.com/YOUR_USERNAME/EduLite.git)
    cd EduLite
    ```

## How to Contribute

### Reporting Bugs

- Check the [GitHub Issues](https://github.com/ibrahim-sisar/EduLite/issues) to see if the bug has already been reported.
- If not, create a new issue.
- Provide a clear title and a detailed description, including:
    - Steps to reproduce the bug.
    - Expected behavior.
    - Actual behavior.
    - Your environment (OS, browser, versions if relevant).
    - Screenshots or error messages if applicable.

### Suggesting Enhancements/Features

- Check the [GitHub Issues](https://github.com/ibrahim-sisar/EduLite/issues) or [Discussions](https://github.com/ibrahim-sisar/EduLite/discussions) to see if your idea has already been discussed.
- If not, create a new issue or start a discussion.
- Clearly describe the proposed enhancement, the problem it solves, and any potential benefits.

### Setting Up Your Development Environment

Our project is a monorepo containing a `backend` (Django) and a `Frontend` (React + Vite). You'll typically want to set up both. For detailed information on each part, please refer to their respective `README.md` files.

#### Backend Setup (Django)

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Apply database migrations:
    ```bash
    python manage.py migrate
    ```
5.  Run the backend development server:
    ```bash
    python manage.py runserver
    ```
    The backend API will usually be available at `http://127.0.0.1:8000/`. Check the `backend/README.md` for more details.

#### Frontend Setup (React + Vite)

1.  Navigate to the frontend project directory:
    ```bash
    cd Frontend/EduLiteFrontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the frontend development server:
    ```bash
    npm run dev
    ```
    The frontend will usually be available at `http://127.0.0.1:5173/` (Vite often picks the next available port if 5173 is busy). Check the `Frontend/README.md` for more details.

### Making Changes (Your First Code Contribution)

1.  **Claim an Issue:** Look for open issues in the [GitHub Issues](https://github.com/ibrahim-sisar/EduLite/issues). If you find one you'd like to work on, comment on it to let others know. If you have a new idea, consider creating an issue first to discuss it.
2.  **Create a Branch:** Create a new branch from the main development branch (e.g., `main` or `develop` - please clarify which branch to base work off).
    * Use a descriptive branch name, for example:
        * `feature/user-authentication`
        * `fix/login-button-bug`
        * `docs/update-readme`
    ```bash
    git checkout -b your-branch-name
    ```
3.  **Write Code:**
    * Write clear, understandable, and well-commented code where necessary.
4.  **Test Your Changes:** (See [Writing Tests](#writing-tests) below).
5.  **Commit Your Changes:**
    * Write clear and concise commit messages. Briefly describe the changes made.
    ```bash
    git add .
    git commit -m "Your descriptive commit message"
    ```

### Writing Tests

We believe that testing is crucial for maintaining a high-quality, stable application.

* **Backend Tests (Django):**
    * Run all backend tests from the `backend/` directory:
        ```bash
        python manage.py test
        ```
    * To run tests for a specific app or class:
        ```bash
        python manage.py test users.tests.test_UserListView
        ```
    * Our preferred test structure is `app_name/tests/test_classname.py` (e.g., `users/tests/test_UserRegistrationView.py`, `users/tests/test_GroupRetrieveView.py`).
    * We encourage using `coverage.py` to check test coverage.
* **Frontend Tests (React):**
    * (TODO: Add instructions for running frontend tests, e.g., `npm test`, and any preferred structure or tools once established).

### Submitting a Pull Request (PR)

1.  Push your branch to your fork on GitHub:
    ```bash
    git push origin your-branch-name
    ```
2.  Go to the EduLite repository on GitHub and click "New pull request".
3.  Choose your branch to compare and create the PR against the project's main development branch.
4.  **Title:** Write a clear, concise PR title (e.g., "Fix: Resolve login button alignment issue" or "Feat: Implement JWT refresh token endpoint").
5.  **Description:**
    * Provide a summary of the changes made.
    * Explain the "why" behind your changes.
    * Link the PR to any relevant issues it resolves (e.g., `Closes #<issue_number>`).
    * Include screenshots or GIFs for UI changes if applicable.
6.  Ensure any CI checks (once configured) pass.

### Code Review Process

* Once a PR is submitted, project maintainers will review it.
* Be prepared for questions and feedback. Constructive criticism is part of the process!
* Make any necessary changes by pushing new commits to your branch. The PR will update automatically.
* Once approved, your PR will be merged. Thank you for your contribution!

### Contributing to Documentation

Good documentation is as important as good code! If you find areas where documentation can be improved (in `README.md` files, inline code comments, or by adding new guides), please feel free to:

* Create an issue to suggest changes.
* Or, create a PR directly with your proposed documentation improvements.

### UI/UX Design Contributions

If you're a UI/UX designer:

* Review existing wireframes (once available) or UI and provide feedback via GitHub Issues or Discussions.
* Propose new designs or improvements for existing interfaces.
* Help create a consistent and user-friendly look and feel for EduLite.

## Coding Standards

* **Python (Backend):**
    * Follow PEP 8 guidelines.
    * Write clear and well-commented code, especially for complex logic.
    * (TODO: Specify any linters like Flake8 or formatters like Black if adopted).
* **JavaScript/React (Frontend):**
    * Follow standard React best practices.
    * (TODO: Specify any linters like ESLint or formatters like Prettier if adopted).
* **General:**
    * Keep code DRY (Don't Repeat Yourself).
    * Ensure your code is readable and maintainable.

## Communication Channels

* **Discord:** [EduLite Discord Server](https://discord.gg/phXnxX2dD4) - For general chat, questions, and collaboration.
* **GitHub Issues:** [EduLite Issues](https://github.com/ibrahim-sisar/EduLite/issues) - For bug tracking and specific feature requests.
* **GitHub Discussions:** [EduLite Discussions](https://github.com/ibrahim-sisar/EduLite/discussions) - For broader ideas, Q&A, and project-wide announcements.

---

Thank you for contributing to EduLite! We appreciate your effort in making education more accessible.

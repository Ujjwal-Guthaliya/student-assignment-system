# StudyFlow — Student Assignment Management System

A Flask-based student assignment management web application with automated CI/CD using GitHub, Jenkins, Docker, and automated tests.

## Overview

StudyFlow helps students manage academic assignments from a single dashboard. Users can register and log in, create assignments, edit and delete them, track completion, and view assignment progress using a modern dark-themed interface.

The project also demonstrates a DevOps workflow in which code pushed to GitHub is automatically detected by Jenkins, tested, packaged into a Docker image, and deployed as a Docker container.

## Features

- User registration and login
- Password hashing using Werkzeug
- Session-based authentication
- Dashboard with assignment statistics
- Add assignments
- Edit assignments
- Delete assignments
- Mark assignment completion/status
- Assignment search
- Status and priority filtering
- Deadline and priority management
- User profile page
- Avatar upload
- Responsive dark UI
- SQLite database
- Automated pytest test suite
- Docker containerization
- Jenkins CI/CD pipeline
- Automatic Jenkins polling for GitHub changes
- Automatic Docker deployment after a successful build

## Technology Stack

### Application
- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2

### Development & DevOps
- Git
- GitHub
- Jenkins
- Docker
- Pytest
- PowerShell

## Project Architecture

```text
Developer
    |
    | git push
    v
GitHub Repository
    |
    | Jenkins Poll SCM
    v
Jenkins
    |
    +--> Checkout
    |
    +--> Install Dependencies
    |
    +--> Run Pytest
    |
    +--> Build Docker Image
    |
    +--> Remove Previous Container
    |
    +--> Run New Docker Container
    |
    v
StudyFlow Application
```

## CI/CD Pipeline

The Jenkins pipeline is defined in `Jenkinsfile`.

Pipeline stages:

1. Checkout source code from GitHub
2. Install Python dependencies
3. Run automated tests
4. Build the Docker image
5. Remove the previous StudyFlow container
6. Start the new container

The application is exposed on port `5000`.

## Automated Testing

Tests are stored in `test_app.py` and use pytest with a temporary SQLite database.

The test suite covers:

- User registration
- User login
- Adding an assignment
- Deleting an assignment

The Jenkins pipeline runs:

```bash
python -m pytest -q
```

## Docker

The application is containerized using the root `Dockerfile`.

Build locally:

```bash
docker build -t studyflow .
```

Run locally:

```bash
docker run -d -p 5000:5000 --name studyflow-app studyflow
```

Then open:

```text
http://localhost:5000
```

## Local Development

Create and activate a Python virtual environment:

```powershell
python -m venv venv
```

If PowerShell blocks `Activate.ps1`, use Command Prompt or adjust the PowerShell execution policy for the current user.

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the application:

```powershell
python app.py
```

Open:

```text
http://localhost:5000
```

## Repository Structure

```text
student-assignment-system/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
├── test_app.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── edit_assignment.html
│   └── profile.html
│
└── static/
    ├── style.css
    ├── script.js
    └── uploads/
```

## How the DevOps Workflow Works

When a developer pushes code to the `main` branch:

```text
Git Push
   ↓
GitHub
   ↓
Jenkins detects SCM change
   ↓
Dependencies installed
   ↓
Pytest
   ↓
Docker image built
   ↓
Old container removed
   ↓
New container started
   ↓
Application updated
```

This demonstrates Continuous Integration and Continuous Deployment (CI/CD).

## Project Objective

The main objective of StudyFlow is to combine a useful student productivity application with a practical DevOps workflow. Instead of deploying the application manually after every code change, Jenkins automates testing, Docker image creation, and deployment.

## Future Improvements

- Persistent Docker volume for SQLite data
- Production database such as PostgreSQL
- Environment variables for secrets
- Better production server configuration
- Email notifications for approaching deadlines
- Cloud deployment
- Role-based administration
- More comprehensive automated tests

## Author

**Ujjwal Kumar**  
B.Tech Information Technology

## Repository

GitHub:
https://github.com/Ujjwal-Guthaliya/student-assignment-system

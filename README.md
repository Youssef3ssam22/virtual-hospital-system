# Virtual Hospital Information System

> **A production-grade hospital management platform built with Python/Django, using Clean Architecture principles with Domain-Driven Design. Includes patient management, lab orders, staff administration, and clinical decision support.**

**Version**: 2.0.0  
**Status**: ✅ Fully Operational

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start](#quick-start)
3. [Starting the System](#starting-the-system)
4. [Authentication](#authentication)
5. [Using the API](#using-the-api)
6. [Modules Overview](#modules-overview)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Architecture](#architecture)

---

## 🖥️ System Requirements

### Minimum Requirements
- **Python**: 3.11+
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB for code + database
- **OS**: Windows 10+, macOS 10.14+, or Linux

### Technologies
- **Backend**: Django 5.0.4 + Django REST Framework 3.15
- **Database**: SQLite (dev) / PostgreSQL 16 (production)
- **Cache**: Redis 7 (optional, for Celery)
- **Async Tasks**: Celery 5.4 (optional)
- **Knowledge Graph**: Neo4j 5 (optional, mock mode default)
- **API Documentation**: Swagger (OpenAPI 3.0) + ReDoc

---

## 🚀 Quick Start

### 1️⃣ Navigate to Project Directory

```bash
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"
```

### 2️⃣ Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment (First Time Only)

```bash
# Copy example configuration
cp .env.example .env

# Optional: Edit .env with your database credentials
# For development, defaults work fine with SQLite
```

### 4️⃣ Initialize Database (First Time Only)

```bash
# Create database tables
python manage.py migrate

# Verify system is healthy
python manage.py check
```

### 5️⃣ Start the System

```bash
# Start development server
python manage.py runserver

# Server will run at: http://localhost:8000
```

---

## 🎯 Starting the System

### Start Command

```bash
python manage.py runserver 0.0.0.0:8000
```

**Expected Output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Access Points

Once server is running:

| **Resource** | **URL** | **Purpose** |
|---|---|---|
| **API Docs (Swagger)** | http://localhost:8000/api/docs/ | Interactive API explorer |
| **API Docs (ReDoc)** | http://localhost:8000/api/redoc/ | Beautiful API documentation |
| **Health Check** | http://localhost:8000/health/ | System status |
| **Django Admin** | http://localhost:8000/admin/ | Database management |

---

## 🔐 Authentication

### Overview
All API endpoints (except `/health/`) require authentication. Staff register and log in using **email** and **password**.

### Step 1: Register a New User

**Method**: `POST`  
**Endpoint**: `/api/v1/auth/register/`

**Using Swagger UI** (Easiest):
1. Open http://localhost:8000/api/docs/
2. Find **Auth** section
3. Click **POST /api/v1/auth/register/**
4. Click **"Try it out"**
5. Fill in the form:
   - `email`: yourname@hospital.com
   - `password`: YourPassword123! (must contain uppercase, number)
   - `full_name`: Your Name
6. Click **Execute**

**Using curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"yourname@hospital.com\",\"password\":\"YourPassword123!\",\"full_name\":\"Your Name\"}"
```

**Using PowerShell**:
```powershell
$body = @{
    email = "yourname@hospital.com"
    password = "YourPassword123!"
    full_name = "Your Name"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

### Step 2: Login to Get Token

**Method**: `POST`  
**Endpoint**: `/api/v1/auth/login/`

**Using curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"yourname@hospital.com\",\"password\":\"YourPassword123!\"}"
```

**Using PowerShell**:
```powershell
$body = @{
    email = "yourname@hospital.com"
    password = "YourPassword123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

**Response**:
```json
{
  "token": "abc123def456...",
  "user": {
    "id": "user-uuid",
    "employee_number": "EMP000100",
    "full_name": "Your Name",
    "role": "DOCTOR"
  }
}
```

### Step 3: Use Token in Requests

Include the token in the `Authorization` header for all subsequent requests:

```bash
curl -X GET http://localhost:8000/api/v1/admin/ ^
  -H "Authorization: Token abc123def456..."
```

---

## 📱 Using the API

### Available Roles

When registering, choose one of these roles:

```
ADMIN           - System Administrator
DOCTOR          - Medical Doctor
NURSE           - Nursing Staff
PHARMACIST      - Pharmacy Staff
LAB_TECHNICIAN  - Lab Technician
RADIOLOGIST     - Radiologist
ACCOUNTANT      - Billing/Accounting
RECEPTIONIST    - Front Desk Staff
```

### Example: Create a Lab Order

**Endpoint**: `POST /api/v1/lab/`

```bash
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\":\"patient-uuid\",\"encounter_id\":\"encounter-uuid\",\"test_codes\":[\"CBC\",\"BMP\"],\"ordered_by\":\"EMP000100\",\"priority\":\"NORMAL\"}"
```

**Response**:
```json
{
  "id": "order-uuid",
  "patient_id": "patient-uuid",
  "encounter_id": "encounter-uuid",
  "test_codes": ["CBC", "BMP"],
  "status": "PENDING",
  "priority": "NORMAL",
  "is_active": true
}
```

### Example: Get Lab Orders

```bash
curl -X GET "http://localhost:8000/api/v1/lab/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 📚 Modules Overview

## 📚 Modules Overview

### ✅ Fully Implemented & Working

#### **Auth Module** (`/api/v1/auth/`)
- User registration and login
- Token-based authentication
- Session management
- Automatic session timeout (8 hours)

#### **Lab Module** (`/api/v1/lab/`) - **RECENTLY FIXED**
- Create lab orders
- Track order status (PENDING → IN_PROGRESS → COMPLETED)
- Store test results
- Query orders by patient or status

#### **Admin Module** (`/api/v1/admin/`)
- Manage administrative staff
- View system configuration
- Access audit logs

#### **Patients Module** (`/api/v1/patients/`)
- Patient registration
- Demographic information
- Allergy tracking
- Patient medical history

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests for Specific Module
```bash
# Lab module
pytest apps/lab/ -v

# Admin module
pytest apps/admin/ -v

# Patients module
pytest apps/patients/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=apps --cov-report=html
# Open htmlcov/index.html to view coverage
```

---

## ❓ Troubleshooting

### Issue: Server won't start

**Error**: `Address already in use`

**Solution**: Port 8000 is in use. Either:
```bash
# Option 1: Use different port
python manage.py runserver 8001

# Option 2: Kill process using port 8000 (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

### Issue: "Database does not exist" / "no such table"

**Error**: `django.db.utils.OperationalError: no such table`

**Solution**: Run migrations
```bash
python manage.py migrate
```

---

### Issue: Authentication fails

**Error**: `401 Unauthorized`

**Solutions**:
1. Verify you have a valid token from login
2. Check token is in `Authorization: Token <token>` header
3. Re-login to get a fresh token if expired

---

### Issue: CORS errors from frontend

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: The default configuration allows:
- `localhost:3000` (React dev server)
- `localhost:5173` (Vite dev server)

To add more origins, edit `.env`:
```
CORS_ALLOWED_ORIGINS=localhost:3000,localhost:5173,your-domain.com
```

---

### Issue: "Module not found" errors

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt
```

---

### Issue: Django check fails

**Error**: `System check identified issues`

**Solution**: View full details and error message
```bash
python manage.py check --deploy
```

---

## 🏗️ Architecture

### Clean Architecture Pattern

```
apps/<module>/
├── domain/           # Pure business logic (no Django)
│   ├── entities.py   # Domain models
│   ├── events.py     # Domain events
│   └── repositories.py  # Repository interfaces
├── application/      # Use cases/orchestration
│   └── use_cases/    # Business flows
├── infrastructure/   # Technical details
│   ├── orm_models.py # Django ORM models
│   └── repositories.py  # Repository implementations
└── interfaces/       # external API
    ├── api/
    │   ├── views.py  # HTTP endpoints
    │   ├── serializers.py  # Request/response format
    │   └── urls.py   # Routes
    └── admin/        # Django Admin config
```

### Key Principles

1. **Domain Layer** - Zero Django imports, pure Python business logic
2. **Dependency Inversion** - Use cases depend on abstract repositories
3. **Event-Driven** - Domain events for state changes
4. **Async Tasks** - Heavy operations via Celery
5. **Thin Views** - Controllers validate input and call one use case

---

## 📊 Project Structure

```
vh_django/
├── config/                  # Settings & URLs
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── dev.py          # Development overrides
│   │   └── prod.py         # Production overrides
│   ├── urls.py             # API routes
│   ├── wsgi.py             # Production server
│   └── celery.py           # Async tasks config
├── apps/                    # Domain modules
│   ├── auth/               # Authentication ✅
│   ├── admin/              # Administration ✅
│   ├── lab/                # Lab Orders ✅
│   ├── patients/           # Patient Management ✅
│   ├── radiology/          # Radiology (skeleton)
│   ├── pharmacy/           # Pharmacy (skeleton)
│   ├── billing/            # Billing (skeleton)
│   └── cdss/               # Clinical Decision Support (skeleton)
├── shared/                  # Shared utilities
│   ├── domain/             # Base classes & exceptions
│   ├── utils/              # Validators, pagination
│   ├── permissions.py      # Permission checks
│   └── constants/          # Global constants
├── infrastructure/         # Technical layer
│   ├── database/           # ORM & repository base
│   ├── event_bus/          # Domain event system
│   ├── audit/              # Audit logging
│   ├── notifications/      # Email/SMS
│   ├── storage/            # File storage
│   ├── tasks/              # Celery tasks
│   └── graph/              # Neo4j client
├── manage.py               # Django CLI
├── conftest.py             # Pytest configuration
├── requirements.txt        # Python dependencies
└── db.sqlite3              # Local SQLite database
```

---

## 🔧 Advanced Features

### Using Celery for Async Tasks (Optional)

```bash
# Start worker
celery -A config worker -l info -Q default,notifications,cdss

# Start scheduler (in another terminal)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Health Check

```bash
curl http://localhost:8000/health/
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-21T19:03:53.402732+00:00",
  "version": "2.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "neo4j": "mock_mode"
  }
}
```

### Environment Variables

Key `.env` variables:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (defaults to SQLite in dev)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Optional: PostgreSQL for production
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=virtual_hospital
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432

# API settings
ADMIN_PASSWORD=Admin@123456
STAFF_DEFAULT_PASSWORD=Hospital@123
CORS_ALLOWED_ORIGINS=localhost:3000,localhost:5173
```

---

## 📱 API Endpoints Quick Reference

| Module     | Endpoint | Method | Purpose |
|---|---|---|---|
| **Auth** | `/api/v1/auth/register/` | POST | Register new user |
| | `/api/v1/auth/login/` | POST | Get authentication token |
| | `/api/v1/auth/logout/` | POST | Logout |
| **Lab** | `/api/v1/lab/` | GET | List lab orders |
| | `/api/v1/lab/` | POST | Create lab order |
| | `/api/v1/lab/{id}/` | GET | Get lab order details |
| **Admin** | `/api/v1/admin/` | GET | List admins |
| | `/api/v1/admin/` | POST | Create admin |
| | `/api/v1/admin/{id}/` | GET | Get admin details |
| **Patients** | `/api/v1/patients/` | GET | List patients |
| | `/api/v1/patients/` | POST | Register patient |
| | `/api/v1/patients/{id}/` | GET | Get patient details |
| **Health** | `/health/` | GET | System status (no auth required) |

---

## 🚀 Deployment to Production

### Using Docker

```bash
# Build images
docker build -t vh-app .

# Start all services
docker-compose up -d

# Check services
docker-compose ps
```

### Using Gunicorn

```bash
# Install
pip install gunicorn

# Run
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 📖 Documentation

- **Interactive API Docs**: http://localhost:8000/api/docs/
- **ReDoc (Markdown Docs)**: http://localhost:8000/api/redoc/
- **FastAPI Testing**: See `API_TESTING.md` in project root
- **Quick Start Guide**: See `QUICKSTART.md` in project root

---

## ✅ Verification Checklist

Before considering the system ready:

- [ ] Server starts without errors: `python manage.py runserver`
- [ ] Health check passes: `curl http://localhost:8000/health/`
- [ ] Can access Swagger: http://localhost:8000/api/docs/
- [ ] Can register user: POST to `/api/v1/auth/register/`
- [ ] Can login: POST to `/api/v1/auth/login/` (get token)
- [ ] Can create lab order: POST to `/api/v1/lab/`
- [ ] Can list lab orders: GET `/api/v1/lab/`
- [ ] Can create admin: POST to `/api/v1/admin/`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] No Django errors: `python manage.py check`

---

## 🆘 Getting Help

1. **Check the docs**: http://localhost:8000/api/docs/ (interactive)
2. **Review error logs**: Check terminal output when server is running
3. **Run health check**: `curl http://localhost:8000/health/`
4. **Check `.env` file**: Verify configuration is correct
5. **Reinstall dependencies**: `pip install -r requirements.txt`

---

## 📄 License

This project is part of a graduation capstone project.

---

## 👥 Support

**For issues or questions:**
1. Check the Troubleshooting section above
2. Review the API documentation at `/api/docs/`
3. Verify database is initialized: `python manage.py migrate`
4. Check server logs for detailed error messages

---

**Last Updated**: March 21, 2026  
**System Status**: ✅ Production Ready
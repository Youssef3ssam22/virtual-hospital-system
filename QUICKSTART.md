# Virtual Hospital System - Quick Start Guide

## 🚀 Starting the System

### Option 1: Run Locally (Recommended for Development)

```bash
# Navigate to project directory
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"

# Start the development server
python manage.py runserver 0.0.0.0:8000
```

The system will start on **http://localhost:8000**

**Expected Output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Option 2: Run with Docker (Full Stack)

```bash
# Navigate to project directory
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"

# Start all services (PostgreSQL, Redis, Neo4j, Web, Celery)
docker-compose up -d

# Check if services are running
docker-compose ps
```

---

## 📚 Accessing the API Documentation

Once the server is running, access the interactive API docs:

### **Swagger UI** (Interactive API Explorer)
- **URL**: http://localhost:8000/api/docs/
- **Features**: Try out API endpoints directly, see request/response examples

### **ReDoc** (Beautiful API Documentation)
- **URL**: http://localhost:8000/api/redoc/
- **Features**: Clean, searchable API documentation

### **Health Check** (System Status)
- **URL**: http://localhost:8000/health/
- **Shows**: Database, Redis, and Neo4j status

---

## 🔐 Authentication

All API endpoints (except `/health/`) require authentication.

### Step 1: Register a New User

**Endpoint**: `POST /api/v1/auth/register/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d {
    "email": "yourname@hospital.com",
    "password": "YourPassword123!",
    "full_name": "John Doe"
  }
```

### Step 2: Login to Get Auth Token

**Endpoint**: `POST /api/v1/auth/login/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d {
    "email": "yourname@hospital.com",
    "password": "YourPassword123!"
  }
```

**Response**:
```json
{
  "token": "your-auth-token-here",
  "user": {
    "id": "user-id",
    "email": "yourname@hospital.com",
    "full_name": "John Doe"
  }
}
```

### Step 3: Use Token in API Requests

For all subsequent API calls, include the Authorization header:

```bash
curl -X GET http://localhost:8000/api/v1/admin/ \
  -H "Authorization: Token your-auth-token-here"
```

---

## 📋 Using the Lab Module (Key Features)

### 1. Create a Lab Order

**Endpoint**: `POST /api/v1/lab/`

```bash
curl -X POST http://localhost:8000/api/v1/lab/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token-here" \
  -d {
    "patient_id": "patient-uuid",
    "encounter_id": "encounter-uuid",
    "test_codes": ["CBC", "BMP", "LFT"],
    "ordered_by": "yourname@hospital.com",
    "priority": "NORMAL",
    "notes": "Routine blood work"
  }
```

**Response**:
```json
{
  "id": "order-uuid",
  "patient_id": "patient-uuid",
  "encounter_id": "encounter-uuid",
  "test_codes": ["CBC", "BMP", "LFT"],
  "ordered_by": "yourname@hospital.com",
  "status": "PENDING",
  "priority": "NORMAL",
  "is_active": true
}
```

### 2. Get Pending Lab Orders

**Endpoint**: `GET /api/v1/lab/?patient_id=patient-uuid`

```bash
curl -X GET "http://localhost:8000/api/v1/lab/?patient_id=patient-uuid" \
  -H "Authorization: Token your-auth-token-here"
```

### 3. Get Specific Lab Order

**Endpoint**: `GET /api/v1/lab/{order_id}/`

```bash
curl -X GET "http://localhost:8000/api/v1/lab/order-uuid/" \
  -H "Authorization: Token your-auth-token-here"
```

---

## 👥 Using the Admin Module

### 1. List All Admins

**Endpoint**: `GET /api/v1/admin/`

```bash
curl -X GET http://localhost:8000/api/v1/admin/ \
  -H "Authorization: Token your-auth-token-here"
```

### 2. Get Specific Admin

**Endpoint**: `GET /api/v1/admin/{admin_id}/`

```bash
curl -X GET "http://localhost:8000/api/v1/admin/admin-uuid/" \
  -H "Authorization: Token your-auth-token-here"
```

### 3. Create New Admin

**Endpoint**: `POST /api/v1/admin/`

```bash
curl -X POST http://localhost:8000/api/v1/admin/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token-here" \
  -d {
    "employee_number": "EMP000200",
    "email": "admin@hospital.com",
    "full_name": "Jane Smith",
    "role": "ADMIN",
    "phone": "555-0100"
  }
```

---

## 🏥 Using the Patients Module

### 1. Register a New Patient

**Endpoint**: `POST /api/v1/patients/`

```bash
curl -X POST http://localhost:8000/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token-here" \
  -d {
    "mrn": "MRN001",
    "first_name": "Patient",
    "last_name": "Name",
    "date_of_birth": "1990-01-15",
    "gender": "M",
    "phone": "555-0001",
    "email": "patient@example.com",
    "address": "123 Main St"
  }
```

### 2. Get Patient Details

**Endpoint**: `GET /api/v1/patients/{patient_id}/`

```bash
curl -X GET "http://localhost:8000/api/v1/patients/patient-uuid/" \
  -H "Authorization: Token your-auth-token-here"
```

### 3. Add Patient Allergy

**Endpoint**: `POST /api/v1/patients/{patient_id}/allergies/`

```bash
curl -X POST "http://localhost:8000/api/v1/patients/patient-uuid/allergies/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token-here" \
  -d {
    "allergen": "Penicillin",
    "reaction": "Anaphylaxis",
    "severity": "SEVERE"
  }
```

---

## 🧪 Running Tests

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
# Lab module tests
python manage.py test apps.lab

# Admin module tests
python manage.py test apps.admin

# Patients module tests
python manage.py test apps.patients
```

### Run with Pytest
```bash
# Raw output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=apps --cov-report=html
```

---

## 🔧 Database Management

### View Database
```bash
# SQLite viewer (dev mode)
# The database is stored in db.sqlite3 (can open with DB Browser for SQLite)
```

### Reset Database (Start Fresh)
```bash
# Delete the database
Remove-Item db.sqlite3 -Force

# Recreate tables
python manage.py migrate
```

### Create Superuser (Django Admin)
```bash
python manage.py createsuperuser

# Access Django Admin at http://localhost:8000/admin/
```

---

## ⚡ Async Tasks (Celery) - Optional

### Start Celery Worker
```bash
celery -A config worker -l info -Q default,notifications,cdss
```

### Start Celery Scheduler (for scheduled tasks)
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 📊 Useful API Query Examples

### Get Pending Lab Orders
```bash
curl -X GET "http://localhost:8000/api/v1/lab/" \
  -H "Authorization: Token token-here"
```

### Get Patient's Lab Orders
```bash
curl -X GET "http://localhost:8000/api/v1/lab/?patient_id=patient-uuid" \
  -H "Authorization: Token token-here"
```

### Filter Active Admins
```bash
curl -X GET "http://localhost:8000/api/v1/admin/" \
  -H "Authorization: Token token-here"
```

---

## 🐛 Troubleshooting

### Server won't start
- **Check**: Port 8000 is not already in use
- **Fix**: `netstat -ano | findstr :8000` then kill process or use different port
- **Alternative**: `python manage.py runserver 8001` (use port 8001)

### Authentication fails
- **Check**: You've called `/api/v1/auth/login/` and got a token
- **Fix**: Ensure token is included in `Authorization: Token <token>` header

### Database errors
- **Check**: Recent migrations applied
- **Fix**: `python manage.py migrate`

### "Table does not exist" error
- **Check**: Migrations haven't been applied
- **Fix**: `python manage.py migrate` then restart server

### CORS Errors (frontend can't connect)
- **Check**: Frontend URL is in CORS_ALLOWED_ORIGINS in settings
- **Default allowed**: `localhost:3000`, `localhost:5173`

---

## 📖 Project Structure

```
vh_django/
├── config/              # Django settings & URLs
├── apps/
│   ├── auth/           # Authentication module
│   ├── admin/          # Admin management module ✅ WORKING
│   ├── lab/            # Lab orders module ✅ WORKING & FIXED
│   ├── patients/       # Patient management module
│   ├── radiology/      # Radiology module (skeleton)
│   ├── pharmacy/       # Pharmacy module (skeleton)
│   ├── billing/        # Billing module (skeleton)
│   └── cdss/           # Clinical Decision Support (skeleton)
├── shared/             # Shared utilities & base classes
├── infrastructure/     # Database, caching, notifications
├── manage.py           # Django management script
└── db.sqlite3          # Local SQLite database (dev)
```

---

## ✅ Quick Verification Checklist

- [ ] Server runs: `python manage.py runserver`
- [ ] Health check passes: Visit http://localhost:8000/health/
- [ ] Can access Swagger: http://localhost:8000/api/docs/
- [ ] Can register user: POST to `/api/v1/auth/register/`
- [ ] Can login: POST to `/api/v1/auth/login/` and get token
- [ ] Can create lab order: POST to `/api/v1/lab/`
- [ ] Can list lab orders: GET `/api/v1/lab/`
- [ ] Can create admin: POST to `/api/v1/admin/`
- [ ] Database migrations applied: `python manage.py migrate`

---

**Need Help?** Check the API documentation at http://localhost:8000/api/docs/ while server is running.

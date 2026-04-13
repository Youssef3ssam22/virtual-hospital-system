# 🏥 Virtual Hospital System - Complete Getting Started Guide

> **Status**: ✅ System Fully Operational | **Last Verified**: March 21, 2026

---

## 📑 Table of Contents

1. [Quick Start (5 Minutes)](#quick-start)
2. [System Architecture](#system-architecture)
3. [Admin Module - Complete Guide](#admin-module)
4. [Lab Module - Complete Guide](#lab-module)
5. [Authentication & Security](#authentication)
6. [API Testing Examples](#api-testing)
7. [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Step 1: Navigate to Project
```bash
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"
```

### Step 2: Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```
**What it does**: Downloads Django, REST Framework, and all dependencies

### Step 3: Initialize Database (First Time Only)
```bash
python manage.py migrate
```
**What it does**: Creates all database tables and schema

### Step 4: Start the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

**✅ System is now running at: http://localhost:8000**

---

## 🏗️ System Architecture

### Technology Stack

```
┌─────────────────────────────────────────┐
│         Frontend Layer                   │
│  (Swagger UI, ReDoc, Web Clients)       │
└────────────────┬────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Django REST Framework API           │
│  (HTTP/JSON Endpoints)                  │
└────────────────┬────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Business Logic (Use Cases)          │
│  🔹 AdminUseCase                        │
│  🔹 LabOrderUseCase                     │
│  🔹 AuthenticationUseCase               │
│  🔹 PatientUseCase                      │
└────────────────┬────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│    Domain Layer (Business Rules)         │
│  - Domain Entities                      │
│  - Domain Events                        │
│  - Validation Logic                     │
└────────────────┬────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│    Infrastructure Layer                  │
│  - Repository Pattern                   │
│  - Database ORM (Django)                │
│  - External Services                    │
└────────────────┬────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│    Data Layer (SQLite / PostgreSQL)      │
└─────────────────────────────────────────┘
```

### Architectural Pattern: **Clean Architecture + DDD**

Each module (`admin`, `lab`, `patients`, etc.) follows:

```
apps/admin/
├── interfaces/          # ← HTTP layer (API views, serializers)
├── application/         # ← Use cases (business logic orchestration)
├── domain/             # ← Business rules (entities, validation)
└── infrastructure/     # ← Database access (repositories, ORM)
```

---

## 👨‍💼 Admin Module - Complete Guide

### Purpose
The Admin Module manages **administrative staff**, **system configuration**, and **audit logs**. Admins control the hospital system and have full access to all features.

### Module Structure
```
apps/admin/
├── domain/
│   ├── entities.py           # Admin entity with business logic
│   ├── repositories.py       # Abstract repository interface
│   └── exceptions.py         # Admin-specific errors
├── infrastructure/
│   ├── models.py             # Django ORM models (database schema)
│   ├── repositories.py       # Concrete repository implementation
│   └── admin.py              # Django admin registration
├── application/
│   ├── use_cases.py          # Business logic (CRUD operations)
│   └── serializers.py        # Request/response validation
└── interfaces/
    └── views.py              # HTTP endpoints
```

### Database Schema (Admin Model)

```
Admin Table
├── id (UUID)                  # Unique identifier
├── employee_number (String)   # Hospital ID
├── email (Email)              # Contact email
├── full_name (String)         # Full name
├── phone (String)             # Phone number
├── department (String)        # Department
├── role (Enum)                # always "ADMIN"
├── is_active (Boolean)        # Account status
├── created_at (DateTime)      # Account creation time
└── updated_at (DateTime)      # Last modification time
```

### API Endpoints

#### 1️⃣ Create New Admin (POST)

**Endpoint**: `POST /api/v1/admin/`

**Required Fields**:
- `email` (required) - Email address
- `full_name` (required) - Full name
- `phone` (optional) - Phone number
- `department` (optional) - Department name

**Example using Swagger UI**:
1. Go to http://localhost:8000/api/docs/
2. Find **Admin** section → **POST /api/v1/admin/**
3. Click **"Try it out"**
4. Fill the form with:
   ```
   email: admin@hospital.com
   full_name: Dr. Ahmed Smith
   phone: 555-0100
   department: Administration
   ```
5. Click **Execute**

**Example using curl**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"email\":\"admin@hospital.com\",\"full_name\":\"Dr. Ahmed Smith\",\"phone\":\"555-0100\",\"department\":\"Administration\"}"
```

**Example using PowerShell**:
```powershell
$body = @{
    email = "admin@hospital.com"
    full_name = "Dr. Ahmed Smith"
    phone = "555-0100"
    department = "Administration"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/" `
    -Method POST `
    -Headers @{"Authorization"="Token YOUR_TOKEN"; "Content-Type"="application/json"} `
    -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

**Successful Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@hospital.com",
  "full_name": "Dr. Ahmed Smith",
  "phone": "555-0100",
  "department": "Administration",
  "employee_number": "ADM0001",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2026-03-21T10:30:00Z",
  "updated_at": "2026-03-21T10:30:00Z"
}
```

---

#### 2️⃣ Get All Admins (GET List)

**Endpoint**: `GET /api/v1/admin/`

**Query Parameters** (optional):
- `search` - Search by name or email
- `is_active` - Filter active/inactive (true/false)
- `page` - Page number for pagination (default: 1)
- `page_size` - Items per page (default: 20)

**Example**:
```bash
# Get all admins
curl -X GET "http://localhost:8000/api/v1/admin/" ^
  -H "Authorization: Token YOUR_TOKEN"

# Search for specific admin
curl -X GET "http://localhost:8000/api/v1/admin/?search=Ahmed" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get only active admins, paginated
curl -X GET "http://localhost:8000/api/v1/admin/?is_active=true&page=1&page_size=10" ^
  -H "Authorization: Token YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/admin/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin1@hospital.com",
      "full_name": "Dr. Ahmed Smith",
      "employee_number": "ADM0001",
      "role": "ADMIN",
      "is_active": true
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "email": "admin2@hospital.com",
      "full_name": "Jane Wilson",
      "employee_number": "ADM0002",
      "role": "ADMIN",
      "is_active": true
    }
  ]
}
```

---

#### 3️⃣ Get Single Admin Details (GET Detail)

**Endpoint**: `GET /api/v1/admin/{admin_id}/`

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@hospital.com",
  "full_name": "Dr. Ahmed Smith",
  "phone": "555-0100",
  "department": "Administration",
  "employee_number": "ADM0001",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2026-03-21T10:30:00Z",
  "updated_at": "2026-03-21T10:30:00Z"
}
```

---

#### 4️⃣ Update Admin (PATCH)

**Endpoint**: `PATCH /api/v1/admin/{admin_id}/`

**Example**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"phone\":\"555-0200\",\"department\":\"IT\"}"
```

---

#### 5️⃣ Delete Admin (DELETE)

**Endpoint**: `DELETE /api/v1/admin/{admin_id}/`

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

### Admin Module Workflow

```
1. USER REGISTERS
   ↓
2. ADMIN LOGIN
   ↓
3. ADMIN CAN:
   ├─→ Create new admin accounts
   ├─→ View all admins
   ├─→ View admin details
   ├─→ Update admin information
   ├─→ Deactivate admin accounts
   └─→ Access audit logs
```

---

## 🧪 Lab Module - Complete Guide

### Purpose
The Lab Module manages **lab orders**, **test samples**, and **lab results**. Lab technicians create orders, process samples, and store test results.

### Module Structure
```
apps/lab/
├── domain/
│   ├── entities.py           # LabOrder, LabResult entities
│   ├── repositories.py       # Abstract repository interface
│   └── exceptions.py         # Lab-specific errors
├── infrastructure/
│   ├── models.py             # Django ORM models
│   ├── repositories.py       # Concrete repository implementation
│   └── admin.py              # Django admin registration
├── application/
│   ├── use_cases.py          # Create, list, update orders
│   └── serializers.py        # Validation
└── interfaces/
    └── views.py              # HTTP endpoints
```

### Database Schema

#### LabOrder Table
```
LabOrder Table
├── id (UUID)                  # Order ID
├── patient_id (UUID)          # Reference to patient
├── encounter_id (UUID)        # Medical encounter
├── test_codes (Array)         # Tests to run: CBC, BMP, LFT, etc.
├── ordered_by (String)        # Doctor email who ordered
├── priority (Enum)            # NORMAL, URGENT, STAT
├── status (Enum)              # PENDING → IN_PROGRESS → COMPLETED
├── notes (Text)               # Special instructions
├── is_active (Boolean)        # Order active status
├── created_at (DateTime)      # Order creation time
└── updated_at (DateTime)      # Last update time
```

#### LabResult Table
```
LabResult Table
├── id (UUID)                  # Result ID
├── order_id (UUID)            # Reference to order
├── test_code (String)         # Test performed
├── result_value (String)      # Test result value
├── unit (String)              # Measurement unit
├── reference_range (String)   # Normal range
├── status (Enum)              # PENDING, COMPLETED, ABNORMAL
├── performed_by (String)      # Technician email
├── created_at (DateTime)      # Result creation time
└── updated_at (DateTime)      # Last update time
```

### Common Lab Test Codes

```
CBC  - Complete Blood Count
BMP  - Basic Metabolic Panel
LFT  - Liver Function Tests
RFT  - Renal Function Tests
UA   - Urinalysis
PT   - Prothrombin Time
PTT  - Partial Thromboplastin Time
```

### API Endpoints

#### 1️⃣ Create Lab Order (POST)

**Endpoint**: `POST /api/v1/lab/`

**Required Fields**:
- `patient_id` (UUID) - Patient identifier
- `encounter_id` (UUID) - Medical encounter
- `test_codes` (array) - Tests to perform: ["CBC", "BMP"]
- `ordered_by` (string) - Doctor email
- `priority` (enum) - NORMAL, URGENT, STAT

**Optional Fields**:
- `notes` (string) - Special instructions

**Example using Swagger UI**:
1. Go to http://localhost:8000/api/docs/
2. Find **Lab** section → **POST /api/v1/lab/**
3. Click **"Try it out"**
4. Use this request body:
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-426614174000",
  "encounter_id": "660e8400-e29b-41d4-a716-426614174000",
  "test_codes": ["CBC", "BMP", "LFT"],
  "ordered_by": "doctor@hospital.com",
  "priority": "NORMAL",
  "notes": "Routine checkup"
}
```
5. Click **Execute**

**Example using curl**:
```bash
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"patient_id\":\"550e8400-e29b-41d4-a716-426614174000\",\"encounter_id\":\"660e8400-e29b-41d4-a716-426614174000\",\"test_codes\":[\"CBC\",\"BMP\"],\"ordered_by\":\"doctor@hospital.com\",\"priority\":\"NORMAL\"}"
```

**Successful Response (201 Created)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "patient_id": "550e8400-e29b-41d4-a716-426614174000",
  "encounter_id": "660e8400-e29b-41d4-a716-426614174000",
  "test_codes": ["CBC", "BMP", "LFT"],
  "ordered_by": "doctor@hospital.com",
  "priority": "NORMAL",
  "status": "PENDING",
  "notes": "Routine checkup",
  "is_active": true,
  "created_at": "2026-03-21T11:00:00Z",
  "updated_at": "2026-03-21T11:00:00Z"
}
```

---

#### 2️⃣ Get All Lab Orders (GET List)

**Endpoint**: `GET /api/v1/lab/`

**Query Parameters**:
- `patient_id` - Filter by patient
- `status` - Filter by status: PENDING, IN_PROGRESS, COMPLETED
- `priority` - Filter by priority: NORMAL, URGENT, STAT
- `page` - Page number
- `page_size` - Items per page

**Example**:
```bash
# Get all orders
curl -X GET "http://localhost:8000/api/v1/lab/" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get pending orders for specific patient
curl -X GET "http://localhost:8000/api/v1/lab/?patient_id=550e8400-e29b-41d4-a716-426614174000&status=PENDING" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get urgent orders
curl -X GET "http://localhost:8000/api/v1/lab/?priority=URGENT" ^
  -H "Authorization: Token YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "patient_id": "550e8400-e29b-41d4-a716-426614174000",
      "test_codes": ["CBC", "BMP"],
      "status": "PENDING",
      "priority": "NORMAL",
      "ordered_by": "doctor@hospital.com",
      "created_at": "2026-03-21T11:00:00Z"
    }
  ]
}
```

---

#### 3️⃣ Get Specific Order (GET Detail)

**Endpoint**: `GET /api/v1/lab/{order_id}/`

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

#### 4️⃣ Update Order Status (PATCH)

**Endpoint**: `PATCH /api/v1/lab/{order_id}/`

**Allowed Status Transitions**:
- PENDING → IN_PROGRESS (lab starts processing)
- IN_PROGRESS → COMPLETED (results available)

**Example**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"status\":\"IN_PROGRESS\"}"
```

---

#### 5️⃣ Add Lab Result (POST Result)

**Endpoint**: `POST /api/v1/lab/{order_id}/add-result/`

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/add-result/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"test_code\":\"CBC\",\"result_value\":\"7.5\",\"unit\":\"10^9/L\",\"reference_range\":\"4.5-11.0\",\"performed_by\":\"tech@hospital.com\"}"
```

---

#### 6️⃣ Get Order Results (GET Order Results)

**Endpoint**: `GET /api/v1/lab/{order_id}/results/`

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/results/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

**Response**:
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "test_code": "CBC",
    "result_value": "7.5",
    "unit": "10^9/L",
    "reference_range": "4.5-11.0",
    "status": "COMPLETED",
    "performed_by": "tech@hospital.com",
    "created_at": "2026-03-21T12:00:00Z"
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440001",
    "test_code": "BMP",
    "result_value": "95",
    "unit": "mg/dL",
    "reference_range": "70-100",
    "status": "COMPLETED",
    "performed_by": "tech@hospital.com",
    "created_at": "2026-03-21T12:05:00Z"
  }
]
```

---

### Lab Module Workflow

```
COMPLETE LAB ORDER WORKFLOW:

1. DOCTOR ORDERS TESTS
   POST /api/v1/lab/
   Status: PENDING
   ↓
   
2. LAB RECEIVES ORDER
   All tests visible in lab queue
   ↓
   
3. LAB STARTS PROCESSING
   PATCH status → IN_PROGRESS
   ↓
   
4. RESULTS COME IN
   POST add-result/ (one per test)
   ↓
   
5. ALL RESULTS ENTERED
   PATCH status → COMPLETED
   ↓
   
6. DOCTOR VIEWS RESULTS
   GET {order_id}/results/
   Results ready for review
```

---

## 🔐 Authentication & Security

### Authentication Workflow

```
1. NEW USER REGISTRATION
   POST /api/v1/auth/register/
   {
     "email": "user@hospital.com",
     "password": "Secure123!",
     "full_name": "User Name"
   }
   ↓
   Response: user created ✓
   
2. USER LOGIN
   POST /api/v1/auth/login/
   {
     "email": "user@hospital.com",
     "password": "Secure123!"
   }
   ↓
   Response: 
   {
     "token": "abc123def456...",
     "user": {...}
   }
   
3. USE TOKEN IN REQUESTS
   -H "Authorization: Token abc123def456..."
   ↓
   API accepts request with full access
```

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 number (0-9)
- At least 1 special character (!@#$%^&*)

---

## 🧪 API Testing Examples

### Complete Test Sequence

**Step 1: Register (if first time)**
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@hospital.com\",\"password\":\"TestPass123!\",\"full_name\":\"Test User\"}"
```

**Step 2: Login**
```bash
# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@hospital.com\",\"password\":\"TestPass123!\"}"
```

Copy the token from response → use as `YOUR_TOKEN` below

**Step 3: Test Admin Module**
```bash
# Create admin
curl -X POST http://localhost:8000/api/v1/admin/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@hospital.com\",\"full_name\":\"Admin User\",\"phone\":\"555-0100\"}"

# List all admins
curl -X GET "http://localhost:8000/api/v1/admin/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

**Step 4: Test Lab Module**
```bash
# Create lab order
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\":\"550e8400-e29b-41d4-a716-426614174000\",\"encounter_id\":\"660e8400-e29b-41d4-a716-426614174000\",\"test_codes\":[\"CBC\"],\"ordered_by\":\"test@hospital.com\",\"priority\":\"NORMAL\"}"

# List lab orders
curl -X GET "http://localhost:8000/api/v1/lab/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

## ❓ Troubleshooting

### Error: "Address already in use" on Port 8000

**Solution**: Either kill the existing process or use a different port:
```bash
# Use port 8001 instead
python manage.py runserver 8001

# Or kill the existing process (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

---

### Error: "401 Unauthorized"

**Possible Causes**:
1. Missing token in header
2. Invalid token format
3. Expired token

**Solution**: 
```bash
# Make sure header is exactly:
-H "Authorization: Token abc123def456..."

# NOT: -H "Authorization: abc123def456..."
# NOT: -H "Token: abc123def456..."
```

---

### Error: "400 Bad Request" on Register

**Possible Causes**:
1. Wrong field names
2. Weak password
3. Invalid email format

**Solution**: Use correct fields:
```json
{
  "email": "user@hospital.com",
  "password": "StrongPass123!",
  "full_name": "Your Name"
}
```

---

### Error: "Database does not exist"

**Solution**: Run migrations
```bash
python manage.py migrate
```

---

## 📊 Health Check

```bash
# Check system health
curl http://localhost:8000/health/

# Expected response:
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok",
  "neo4j": "mock_mode"
}
```

---

## 🗺️ API Documentation URLs

Once server is running:

| Resource | URL |
|----------|-----|
| **Interactive API (Start Here!)** | http://localhost:8000/api/docs/ |
| Beautiful Docs | http://localhost:8000/api/redoc/ |
| Health Check | http://localhost:8000/health |
| Django Admin | http://localhost:8000/admin |

---

## ✅ Verification Checklist

Navigate through each of these to verify everything works:

- [ ] Server started: `python manage.py runserver`
- [ ] Health check passes: GET /health/
- [ ] Can register user: POST /auth/register/
- [ ] Can login: POST /auth/login/
- [ ] Can create admin: POST /admin/
- [ ] Can list admins: GET /admin/
- [ ] Can create lab order: POST /lab/
- [ ] Can list lab orders: GET /lab/
- [ ] Can view API docs: http://localhost:8000/api/docs/

---

**First Time Setup Complete! 🎉**

You now have a fully operational hospital management system ready for development and testing.

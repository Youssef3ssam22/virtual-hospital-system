# 📖 Virtual Hospital System - Documentation Guide

> **Generated**: March 21, 2026  
> **System Status**: ✅ Fully Operational & Documented

---

## 📚 Complete Documentation

This system comes with comprehensive documentation. Here's which guide to use:

### 1️⃣ **START HERE** → [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md)
   - **Purpose**: Ultimate reference guide for everything
   - **Contains**: System architecture, admin module, lab module, API examples
   - **Best For**: First-time setup, understanding how everything works
   - **Length**: Comprehensive (long but complete)
   - **Audience**: Everyone

---

### 2️⃣ [GETTING_STARTED.md](./GETTING_STARTED.md)
   - **Purpose**: 5-minute quick start
   - **Contains**: Quick commands, first login, basic testing
   - **Best For**: New users who just want to get running fast
   - **Length**: Short and simple
   - **Audience**: Complete beginners

---

### 3️⃣ [SETUP.md](./SETUP.md)
   - **Purpose**: Command reference card
   - **Contains**: Copy-paste commands, common tasks, troubleshooting
   - **Best For**: Quick reference during development
   - **Length**: Command-focused
   - **Audience**: Developers

---

### 4️⃣ [QUICKSTART.md](./QUICKSTART.md)
   - **Purpose**: Feature walkthroughs
   - **Contains**: Lab orders, admin operations, patient management
   - **Best For**: Learning specific features
   - **Length**: Medium
   - **Audience**: Power users

---

### 5️⃣ [API_TESTING.md](./API_TESTING.md)
   - **Purpose**: API testing methods
   - **Contains**: curl, PowerShell, Python examples
   - **Best For**: Testing and debugging APIs
   - **Length**: Short with code examples
   - **Audience**: Developers

---

### 6️⃣ [README.md](./README.md)
   - **Purpose**: Professional project overview
   - **Contains**: System requirements, architecture, modules overview
   - **Best For**: Understanding the project structure
   - **Length**: Medium
   - **Audience**: Project stakeholders

---

## 🚀 Quick Navigation

### I want to...

#### **Get the system running**
→ Follow [GETTING_STARTED.md](./GETTING_STARTED.md) (5-10 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
python manage.py migrate

# 3. Start server
python manage.py runserver
```

---

#### **Understand the Architecture**
→ Read [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) → System Architecture section

```
Clean Architecture + Domain-Driven Design

Domain Layer (Business Rules)
    ↓
Application Layer (Use Cases)
    ↓
Infrastructure Layer (Repositories)
    ↓
Interfaces Layer (HTTP APIs)
    ↓
Presentation (Swagger UI)
```

---

#### **Use the Admin Module**
→ Read [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) → Admin Module section

**Quick Reference**:
```bash
# Create admin
POST /api/v1/admin/
{
  "email": "admin@hospital.com",
  "full_name": "Dr. Ahmed Smith",
  "phone": "555-0100"
}

# List admins
GET /api/v1/admin/

# Get admin details
GET /api/v1/admin/{admin_id}/

# Update admin
PATCH /api/v1/admin/{admin_id}/

# Delete admin
DELETE /api/v1/admin/{admin_id}/
```

---

#### **Use the Lab Module**
→ Read [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) → Lab Module section

**Quick Reference**:
```bash
# Create lab order
POST /api/v1/lab/
{
  "patient_id": "uuid",
  "encounter_id": "uuid",
  "test_codes": ["CBC", "BMP"],
  "ordered_by": "doctor@hospital.com",
  "priority": "NORMAL"
}

# List orders
GET /api/v1/lab/

# Get order details
GET /api/v1/lab/{order_id}/

# Update order status
PATCH /api/v1/lab/{order_id}/

# Add result
POST /api/v1/lab/{order_id}/add-result/

# Get results
GET /api/v1/lab/{order_id}/results/
```

---

#### **Test the API**
→ Follow [API_TESTING.md](./API_TESTING.md)

**3 Methods**:
1. **Swagger UI** (Easiest) → http://localhost:8000/api/docs/
2. **Command Line** (curl/PowerShell) → See API_TESTING.md
3. **Python Script** → Run verify_system.py

---

#### **List Common Commands**
→ Check [SETUP.md](./SETUP.md) → Common Commands Reference

---

## 📊 Module Overview

### ✅ Implemented & Working

| Module | Purpose | Status |
|--------|---------|--------|
| **Auth** | User registration & login | ✅ Full |
| **Admin** | Admin staff management | ✅ Full |
| **Lab** | Lab orders & results | ✅ Full |
| **Patients** | Patient data & allergies | ✅ Full |

---

### 🔄 Lab Module Workflow

```
Step 1: Doctor Orders Tests
┌─────────────────────────────────┐
│ POST /api/v1/lab/               │
│ Creates lab order (PENDING)     │
└────────────┬────────────────────┘
             │
Step 2: Lab Receives Order
┌────────────▼────────────────────┐
│ GET /api/v1/lab/                │
│ Lab technician sees new orders  │
└────────────┬────────────────────┘
             │
Step 3: Lab Starts Processing
┌────────────▼────────────────────┐
│ PATCH /api/v1/lab/{id}/         │
│ Change status to IN_PROGRESS    │
└────────────┬────────────────────┘
             │
Step 4: Results Arrive
┌────────────▼────────────────────┐
│ POST /api/v1/lab/{id}/add-result/
│ Add each test result            │
└────────────┬────────────────────┘
             │
Step 5: Mark Complete
┌────────────▼────────────────────┐
│ PATCH /api/v1/lab/{id}/         │
│ Change status to COMPLETED      │
└────────────┬────────────────────┘
             │
Step 6: Doctor Reviews Results
┌────────────▼────────────────────┐
│ GET /api/v1/lab/{id}/results/   │
│ Doctor sees all test results    │
└─────────────────────────────────┘
```

---

### 👨‍💼 Admin Module Workflow

```
Admin Operations:

1. CREATE ADMIN
   POST /api/v1/admin/
   │
   ├─ Email
   ├─ Full Name
   ├─ Phone
   └─ Department
   ↓
2. LIST ALL ADMINS
   GET /api/v1/admin/
   ↓
3. VIEW ADMIN DETAILS
   GET /api/v1/admin/{id}/
   ↓
4. UPDATE INFO
   PATCH /api/v1/admin/{id}/
   ↓
5. DEACTIVATE
   DELETE /api/v1/admin/{id}/
```

---

## 🔑 Authentication Fields

### Registration
```json
{
  "email": "user@hospital.com",          ← Email address (required)
  "password": "StrongPass123!",          ← Min 8 chars, 1 uppercase, 1 number, 1 special
  "full_name": "User Name"               ← Full name (required)
}
```

### Login
```json
{
  "email": "user@hospital.com",          ← Email from registration
  "password": "StrongPass123!"           ← Corresponding password
}
```

### Using Token
```bash
-H "Authorization: Token abc123def456..."
```

---

## 🌐 Access Points

| Resource | URL | Purpose |
|----------|-----|---------|
| **Interactive API** | http://localhost:8000/api/docs/ | Try endpoints live |
| **Beautiful Docs** | http://localhost:8000/api/redoc/ | Read documentation |
| **Health Check** | http://localhost:8000/health/ | System status |
| **Django Admin** | http://localhost:8000/admin/ | Database management |

---

## ⚠️ Common Issues & Solutions

### "Address already in use"
```bash
# Use different port
python manage.py runserver 8001
```

### "400 Bad Request"
```bash
# Wrong fields used. Use CORRECT fields:
✓ email, password, full_name (NOT employee_number)
✓ Use "Authorization: Token" (NOT "Bearer")
```

### "401 Unauthorized"
```bash
# Token missing or invalid
✓ Include Authorization header
✓ Use format: "Token abc123..."
✓ Token valid (not expired)
```

### "No such table"
```bash
# Forgot to run migrations
python manage.py migrate
```

---

## 🧪 Verification

Run the system verification script:
```bash
python verify_system.py
```

This will:
- ✅ Check server connectivity
- ✅ Test registration & login
- ✅ Test admin CRUD operations
- ✅ Test lab order CRUD operations
- ✅ Verify API documentation

---

## 📝 Database

### Location
- **Development**: `db.sqlite3` (in project root)
- **Production**: PostgreSQL 16

### Resetting Database
```bash
# Delete database
Remove-Item -Force db.sqlite3

# Recreate
python manage.py migrate
```

---

## 🎓 Learning Path

### For Beginners
1. Read [GETTING_STARTED.md](./GETTING_STARTED.md)
2. Follow the 5-minute quick start
3. Open http://localhost:8000/api/docs/
4. Try register and login in Swagger UI
5. Explore endpoints in Swagger UI

### For Developers
1. Read [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) → System Architecture
2. Understand Clean Architecture + DDD pattern
3. Study [QUICKSTART.md](./QUICKSTART.md) → Feature walkthroughs
4. Use [API_TESTING.md](./API_TESTING.md) for advanced testing
5. Explore code in `apps/admin/` and `apps/lab/`

### For System Admins
1. Read [README.md](./README.md) → System Requirements
2. Follow setup in [GETTING_STARTED.md](./GETTING_STARTED.md)
3. Use [SETUP.md](./SETUP.md) for common commands
4. Monitor health: GET /health/
5. Manage users in Django admin

---

## ✅ Final Checklist

Before using the system:

- [ ] Python 3.11+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database initialized: `python manage.py migrate`
- [ ] Server started: `python manage.py runserver`
- [ ] Health check passes: GET /health/
- [ ] Can access API docs: http://localhost:8000/api/docs/
- [ ] Can register user
- [ ] Can login and get token

---

## 🎉 You're All Set!

Your Virtual Hospital System is ready to use. Start with [GETTING_STARTED.md](./GETTING_STARTED.md) and refer to [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) for detailed information about each module.

**Questions?** Check the relevant documentation file or use the troubleshooting sections.

**Happy coding! 🚀**

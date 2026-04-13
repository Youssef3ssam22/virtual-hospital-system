# Setup & Running Guide - Quick Reference

## 🚀 Quick Start (Copy & Paste Steps)

### Step 1: Navigate to Project
```bash
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"
```

### Step 2: Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

### Step 3: Setup Database (First Time Only)
```bash
python manage.py migrate
python manage.py check
```

### Step 4: Start the Server
```bash
python manage.py runserver
```

**✅ Server is now running at: http://localhost:8000**

---

## 📂 Important URLs

| What | URL | Notes |
|---|---|---|
| **Interactive API** | http://localhost:8000/api/docs/ | Try out endpoints here |
| **API Docs** | http://localhost:8000/api/redoc/ | Beautiful documentation |
| **System Health** | http://localhost:8000/health/ | Check if everything is running |
| **Django Admin** | http://localhost:8000/admin/ | Database management |

---

## 🔐 First Time Setup - Register & Login

### 1. Register a User

Open **http://localhost:8000/api/docs/** (easiest way!)

Or use curl:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@hospital.com\",\"password\":\"MyPass123!\",\"full_name\":\"My Name\"}"
```

### 2. Login to Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@hospital.com\",\"password\":\"MyPass123!\"}"
```

Copy the `token` from the response.

### 3. Use Token in API Calls

```bash
curl -X GET http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## 🧪 Test API - Lab Module Example

### Create Lab Order
```bash
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\":\"123e4567-e89b-12d3-a456-426614174000\",\"encounter_id\":\"223e4567-e89b-12d3-a456-426614174000\",\"test_codes\":[\"CBC\"],\"ordered_by\":\"user@hospital.com\",\"priority\":\"NORMAL\"}"
```

### Get All Lab Orders
```bash
curl -X GET http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

## ⚡ Common Commands Reference

| Task | Command |
|---|---|
| **Start server** | `python manage.py runserver` |
| **Check system** | `python manage.py check` |
| **Run migrations** | `python manage.py migrate` |
| **Create superuser** | `python manage.py createsuperuser` |
| **Run tests** | `pytest tests/ -v` |
| **Reset database** | `Remove-Item db.sqlite3` then `python manage.py migrate` |
| **Django shell** | `python manage.py shell` |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| **"Address already in use"** | Kill process: `python manage.py runserver 8001` (use port 8001 instead) |
| **"no such table"** | Run: `python manage.py migrate` |
| **"Module not found"** | Run: `pip install -r requirements.txt` |
| **"401 Unauthorized"** | Get new token from login endpoint |
| **Server won't start** | Run: `python manage.py check` to see errors |

---

## 💡 Available Roles for Registration

```
ADMIN           Admin user
DOCTOR          Medical doctor
NURSE           Nursing staff
PHARMACIST      Pharmacy staff
LAB_TECHNICIAN  Lab technician
RADIOLOGIST     Radiologist
ACCOUNTANT      Accounting/billing
RECEPTIONIST    Front desk
```

---

## ✅ System Check Verification

After starting the server, verify everything works:

1. **Health Check**:
   ```bash
   curl http://localhost:8000/health/
   ```
   Should return status `200` with `"status": "healthy"`

2. **API Docs**:
   Visit http://localhost:8000/api/docs/ - should load without errors

3. **Registration**:
   Try creating a new user through Swagger UI

4. **Login**:
   Try logging in and getting a token

---

## 📁 Project Structure (Key Folders)

```
apps/
├── auth/       - Login/Register (READY)
├── admin/      - Admin management (READY)
├── lab/        - Lab orders (READY - FIXED)
├── patients/   - Patient management (READY)
└── radiology/, pharmacy/, billing/, cdss/  (skeleton modules)

config/        - Settings & URLs
shared/        - Shared utilities
infrastructure/- Database, caching, notifications
```

---

## 🎯 What's Already Working

✅ **Authentication System** - Register & Login  
✅ **Lab Module** - Create/View lab orders (FIXED!)  
✅ **Admin Module** - Manage admin users  
✅ **Patients Module** - Register & manage patients  
✅ **API Documentation** - Swagger + ReDoc  
✅ **Database** - SQLite initialized with all tables  

---

## 📝 Environment File (.env)

Most settings work with defaults. Optional changes:

```ini
# Change if needed
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key

# Optional: Setup PostgreSQL instead of SQLite
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=virtual_hospital
# DB_USER=postgres
# DB_PASSWORD=your-password
```

---

## 🆘 Need Help?

1. Check the **full README.md** for detailed docs
2. Open **http://localhost:8000/api/docs/** for interactive API explorer
3. Review **API_TESTING.md** for API testing examples
4. Check console output when server is running for error messages

---

**Ready to Start?** Navigate to project and run: `python manage.py runserver` ✅

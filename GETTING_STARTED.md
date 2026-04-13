# 🚀 Getting Started - Virtual Hospital System

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ Python 3.11+ installed
- ✅ Project files downloaded
- ✅ Internet connection (first time to download dependencies)

---

## ⚡ 5-Minute Quick Start

### Step 1️⃣: Open PowerShell/Terminal

```bash
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"
```

### Step 2️⃣: Install Dependencies (First Time Only - 2 min)

```bash
pip install -r requirements.txt
```

**What it does**: Downloads and installs all required libraries (Django, REST Framework, etc.)

### Step 3️⃣: Setup Database (First Time Only - 30 sec)

```bash
python manage.py migrate
```

**What it does**: Creates database tables and initializes the system

### Step 4️⃣: Start the Server (Every Time)

```bash
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### ✅ You're Done! The system is running!

---

## 🌐 Access the System

Once the server is running, open these in your browser:

### **Easiest Way to Test:**
👉 **Go to: http://localhost:8000/api/docs/**

This is the interactive API explorer. You can:
1. Register a new user
2. Login to get a token
3. Test any API endpoint
4. See real-time responses

### **Other Access Points:**

| Link | Purpose |
|---|---|
| **http://localhost:8000/api/docs/** | 🎯 **START HERE** - Interactive API |
| http://localhost:8000/api/redoc/ | Beautiful documentation |
| http://localhost:8000/health/ | System status check |
| http://localhost:8000/admin/ | Database management |

---

## 🔐 Your First Login

### Option A: Using Swagger UI (Recommended - Easiest!)

1. Open **http://localhost:8000/api/docs/**
2. Scroll to **Auth** section
3. Click **POST /api/v1/auth/register/**
4. Click **"Try it out"**
5. Fill in the form:
   - Email: `yourname@hospital.com`
   - Password: `MySecurePassword123!`
   - Full Name: `Your Name`
6. Click **Execute**
7. You'll see the response with your user created ✅

### Option B: Using Command Line

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"yourname@hospital.com\",\"password\":\"MySecurePassword123!\",\"full_name\":\"Your Name\"}"

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"yourname@hospital.com\",\"password\":\"MySecurePassword123!\"}"
```

---

## 🧪 Testing the System

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/api/docs/
2. Login using the endpoint in **Auth** section
3. Copy the token from login response
4. Click **Authorize** button (top right)
5. Paste: `Token <your-token-here>` in the dialog
6. Now you can test all endpoints!

### Test Create Lab Order

1. Go to **Lab** section
2. Click **POST /api/v1/lab/**
3. Click **"Try it out"**
4. Paste this in the request body:
```json
{
  "patient_id": "123e4567-e89b-12d3-a456-426614174000",
  "encounter_id": "223e4567-e89b-12d3-a456-426614174000",
  "test_codes": ["CBC", "BMP"],
  "ordered_by": "yourname@hospital.com",
  "priority": "NORMAL"
}
```
5. Click **Execute** → See response ✅

---

## 📚 Documentation Files

In the project folder, you'll find:

| File | Purpose |
|---|---|
| **README.md** | 📖 Full professional documentation |
| **SETUP.md** | ⚙️ Quick reference commands |
| **API_TESTING.md** | 🧪 API testing examples |
| **QUICKSTART.md** | 🚀 Feature walkthroughs |

---

## 🛑 Stopping the Server

When you want to stop:
1. Press **CTRL + C** in the terminal running the server
2. Server will stop gracefully

---

## 🔄 Restarting the System

Each time you want to restart:

```bash
# Open terminal
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"

# Start server
python manage.py runserver
```

**Note**: Database and all data persist, so you don't need to re-run migrate

---

## ❌ If Something Goes Wrong

### Server Won't Start

```bash
# Check what's wrong
python manage.py check

# If "Address already in use", use different port
python manage.py runserver 8001
# Then access: http://localhost:8001
```

### Database Errors

```bash
# Reset database (deletes all data!)
Remove-Item db.sqlite3

# Reinitialize
python manage.py migrate

# Restart server
python manage.py runserver
```

### Missing Dependencies

```bash
# Reinstall
pip install -r requirements.txt
```

---

## 🎯 Available Roles

When registering, use one of:

```
ADMIN           → System Administrator
DOCTOR          → Medical Doctor
NURSE           → Nursing Staff
PHARMACIST      → Pharmacy Staff
LAB_TECHNICIAN  → Lab Technician
RADIOLOGIST     → Radiologist
ACCOUNTANT      → Billing/Accounting
RECEPTIONIST    → Front Desk
```

---

## ✅ Quick Verification

After starting server, verify everything works:

1. **Health Check**: Visit http://localhost:8000/health/
   - Should show: `"status": "healthy"`

2. **API Docs Load**: http://localhost:8000/api/docs/
   - Should load without errors

3. **Can Register**: Try registering via Swagger

4. **Can Login**: Try logging in and getting token

5. **Can Call API**: Get admin list with token

---

## 💡 Tips & Tricks

### Save Time Testing
- Use Swagger UI (http://localhost:8000/api/docs/) instead of command line
- No need to format JSON or escape quotes
- Can see real-time responses

### Keep Token Handy
- After login in Swagger, token is shown in response
- Click **Authorize** to auto-add to all requests
- Or copy-paste for command line tests

### Database Stays Between Restarts
- Data persists when you stop/start server
- Only lost if you delete `db.sqlite3` file
- Good for testing without re-creating users

### Run Tests
```bash
pytest tests/ -v
```
All tests should pass ✅

---

## 📞 Troubleshooting

| Issue | Fix |
|---|---|
| **"Python not found"** | Install Python 3.11+ from python.org |
| **"pip not found"** | Use `python -m pip` instead |
| **"Address already in use"** | Use `python manage.py runserver 8001` |
| **"Database error"** | Run `python manage.py migrate` |
| **"403 Unauthorized"** | Need to login and include token in request |
| **"Module not found"** | Run `pip install -r requirements.txt` |

---

## 🎓 What's Included

### ✅ Working Modules

1. **Authentication** - Register, Login, Token Management
2. **Lab Module** - Create/View lab orders **(FIXED)**
3. **Administrative** - Manage admin users and configuration
4. **Patients** - Register and manage patients
5. **API Documentation** - Interactive Swagger + ReDoc

### 📊 Infrastructure

- SQLite Database (auto-created)
- REST API with DRF
- Clean Architecture Design
- Comprehensive Error Handling
- API Documentation Auto-generation

### 🧪 Testing

- Unit & Integration Tests included
- Test fixtures and factories
- Can run with: `pytest tests/ -v`

---

## 🚀 Next Steps

1. **Start the server** ← You are here
2. **Register a user** - Use Swagger UI
3. **Login to get token** - Copy from response
4. **Test API endpoints** - Try creating lab orders
5. **Read full docs** - Check README.md for advanced features
6. **Customize** - Modify URLs, add more modules, etc.

---

## 📖 Quick Reference

```bash
# Navigate to project
cd "d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django"

# Install (first time)
pip install -r requirements.txt

# Setup database (first time)
python manage.py migrate

# Run server (every time)
python manage.py runserver

# Then open:
http://localhost:8000/api/docs/
```

---

## 🎉 You're All Set!

Your Virtual Hospital System is ready to use.

**Next**: Open http://localhost:8000/api/docs/ and start testing! 

**Questions?** Check:
- README.md - Full documentation
- API_TESTING.md - API examples
- SETUP.md - Command reference

---

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: March 21, 2026

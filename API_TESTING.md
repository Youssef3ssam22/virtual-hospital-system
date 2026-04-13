# API Testing Guide - Register & Login User

## ✅ Method 1: Using curl (Recommended - Works on Windows 10+)

### Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"user@hospital.com\", \"password\": \"SecurePass123!\", \"full_name\": \"John Doe\"}"
```

**Windows Note**: Use `^` at end of line to continue to next line (instead of `\`)

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"user@hospital.com\", \"password\": \"SecurePass123!\"}"
```

---

## ✅ Method 2: Using PowerShell Invoke-WebRequest

### Register a New User
```powershell
$body = @{
    email = "user@hospital.com"
    password = "SecurePass123!"
    full_name = "John Doe"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

### Login
```powershell
$body = @{
    email = "user@hospital.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

# Extract token
$token = ($response.Content | ConvertFrom-Json).token
Write-Host "Your Token: $token"
```

---

## ✅ Method 3: Using Python (Best for Complex Testing)

Create a file called `auth_test.py`:

```python
#!/usr/bin/env python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register a new user
print("=" * 50)
print("1. REGISTER NEW USER")
print("=" * 50)

register_data = {
    "email": "user@hospital.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}

print("\nRequest Data:")
print(json.dumps(register_data, indent=2))

response = requests.post(
    f"{BASE_URL}/auth/register/",
    json=register_data,
    headers={"Content-Type": "application/json"}
)

print(f"\nStatus Code: {response.status_code}")
print("Response:")
print(json.dumps(response.json(), indent=2))

# 2. Login
print("\n" + "=" * 50)
print("2. LOGIN")
print("=" * 50)

login_data = {
    "email": "user@hospital.com",
    "password": "SecurePass123!"
}

print("\nRequest Data:")
print(json.dumps(login_data, indent=2))

response = requests.post(
    f"{BASE_URL}/auth/login/",
    json=login_data,
    headers={"Content-Type": "application/json"}
)

print(f"\nStatus Code: {response.status_code}")
print("Response:")
data = response.json()
print(json.dumps(data, indent=2))

# Save token for next requests
if response.status_code == 200:
    token = data.get("token")
    print(f"\n✅ Token saved: {token}")
    
    # 3. Test authenticated request
    print("\n" + "=" * 50)
    print("3. GET ADMIN LIST (Authenticated)")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/admin/",
        headers=headers
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
```

Run it:
```bash
python auth_test.py
```

---

## 📝 Available Roles

When registering, use one of these roles:

```
ADMIN          - System Administrator
DOCTOR         - Medical Doctor
NURSE          - Nursing Staff
PHARMACIST     - Pharmacy Staff
LAB_TECHNICIAN - Lab Technician
RADIOLOGIST    - Radiologist
ACCOUNTANT     - Billing/Accounting Staff
RECEPTIONIST   - Receptionist
```

---

## 🔑 API Response Format

### Successful Registration (201)
```json
{
  "id": "user-uuid",
  "email": "user@hospital.com",
  "full_name": "John Doe",
  "is_active": true
}
```

### Successful Login (200)
```json
{
  "token": "abcdef123456...",
  "user": {
    "id": "user-uuid",
    "email": "user@hospital.com",
    "full_name": "John Doe"
  }
}
```

### Error (400/409)
```json
{
  "error": "Email already exists" or other error message
}
```

---

## 🎯 Quick Test - Copy & Paste Ready

### Using curl (Fastest)
```bash
# REGISTER
curl -X POST http://localhost:8000/api/v1/auth/register/ -H "Content-Type: application/json" -d "{\"employee_number\":\"EMP000100\",\"password\":\"Test123!\",\"full_name\":\"Test User\",\"role\":\"DOCTOR\"}"

# LOGIN (save the token from response)
curl -X POST http://localhost:8000/api/v1/auth/login/ -H "Content-Type: application/json" -d "{\"employee_number\":\"EMP000100\",\"password\":\"Test123!\"}"

# GET ADMIN LIST (replace TOKEN_HERE with your token)
curl -X GET http://localhost:8000/api/v1/admin/ -H "Authorization: Token TOKEN_HERE"
```

---

## ✅ Step-by-Step from PowerShell

1. **Open PowerShell** in the project directory

2. **Start the server** (if not already running):
```powershell
python manage.py runserver
```

3. **In a new PowerShell window, register a user**:
```powershell
$body = @{
    employee_number = "YOUSSEF001"
    password = "MyPassword123!"
    full_name = "Youssef"
    role = "DOCTOR"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body `
    -UseBasicParsing

$response.Content
```

4. **Login to get token**:
```powershell
$body = @{
    employee_number = "YOUSSEF001"
    password = "MyPassword123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login/" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body `
    -UseBasicParsing

$response.Content
```

5. **Copy the token from response and use it**:
```powershell
$token = "your-token-from-response"

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/" `
    -Method GET `
    -Headers @{"Authorization"="Token $token"} `
    -UseBasicParsing

$response.Content
```

---

## 🌐 Using Swagger UI (Interactive - Easiest!)

1. Go to: **http://localhost:8000/api/docs/**
2. Look for **Auth** section
3. Click on **`POST /api/v1/auth/register/`**
4. Click **"Try it out"** (blue button)
5. Fill in the form and click **Execute**
6. Repeat for login
7. Copy the token and use it in other endpoints!

---

## ⚡ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `curl: command not found` | Install Windows Terminal or use PowerShell method |
| `SSL certificate error` | Add `-k` flag to curl: `curl -k -X POST ...` |
| `Connection refused` | Make sure server is running: `python manage.py runserver` |
| `401 Unauthorized` | Token missing or expired - re-login |
| `400 Bad Request` | Check JSON formatting (use double quotes, escape properly) |
| `409 Conflict` | Employee number already exists - use different one |

---

## 💡 Pro Tips

- **Save token in variable**: Makes it easier to reuse for multiple requests
- **Use Swagger UI**: Fastest way to test while developing
- **Keep employee numbers unique**: Can't have duplicates
- **Test with curl first**: Simplest for quick tests
- **Use Python script**: Best for automated testing

---

**Need Help?** Open **http://localhost:8000/api/docs/** while server is running - it has an interactive interface where you can test all endpoints!

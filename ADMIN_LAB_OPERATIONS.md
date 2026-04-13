# 🎯 Admin & Lab Modules - Detailed Operations Guide

> **Purpose**: Step-by-step guide for Admin and Lab module operations  
> **Audience**: End users, developers, testers

---

## 📋 Table of Contents

1. [Admin Module - Detailed Operations](#admin-module)
2. [Lab Module - Detailed Operations](#lab-module)
3. [Integration Examples](#integration-examples)
4. [Error Handling](#error-handling)

---

## 👨‍💼 Admin Module

### What is the Admin Module?

The Admin Module manages **hospital administrative staff**. It stores information about:
- Admin user accounts
- Contact information
- Department assignments
- Active/inactive status

**Key Characteristics**:
- All admins have `role: ADMIN`
- Automatic `employee_number` generation
- Full CRUD operations (Create, Read, Update, Delete)
- Search and filtering capability

---

### Operation 1: Create a New Admin

#### Purpose
Register a new administrative staff member in the system.

#### Data Required
| Field | Type | Required | Example |
|-------|------|----------|---------|
| email | String | ✅ Yes | admin@hospital.com |
| full_name | String | ✅ Yes | Dr. Ahmed Smith |
| phone | String | ❌ No | 555-0100 |
| department | String | ❌ No | Administration |

#### Step-by-Step via Swagger UI

1. **Open API Documentation**
   - Navigate to: http://localhost:8000/api/docs/
   - Scroll down to **Admin** section
   - Look for blue **POST** button with `/api/v1/admin/`

2. **Click "Try it out"**
   - The request body editor will appear

3. **Fill in the Request**
   ```json
   {
     "email": "admin@hospital.com",
     "full_name": "Dr. Ahmed Smith",
     "phone": "555-0100",
     "department": "Administration"
   }
   ```

4. **Click "Execute"**
   - Wait for response
   - You'll see status `201 Created` if successful

5. **Review Response**
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
     "created_at": "2026-03-21T10:30:00Z"
   }
   ```
   - **Note**: `employee_number` is automatically generated!

---

#### Step-by-Step via curl

```bash
# Copy and paste this entire command (Windows):
curl -X POST http://localhost:8000/api/v1/admin/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"email\":\"admin@hospital.com\",\"full_name\":\"Dr. Ahmed Smith\",\"phone\":\"555-0100\",\"department\":\"Administration\"}"
```

**Explanation of each part**:
- `curl -X POST` → Send HTTP POST request
- `http://localhost:8000/api/v1/admin/` → API endpoint
- `-H "Content-Type: application/json"` → Request is JSON format
- `-H "Authorization: Token YOUR_TOKEN"` → Your authentication token
- `-d "..."` → The request body with admin data

---

#### Step-by-Step via PowerShell

```powershell
# Create the request body
$body = @{
    email = "admin@hospital.com"
    full_name = "Dr. Ahmed Smith"
    phone = "555-0100"
    department = "Administration"
} | ConvertTo-Json

# Send the request
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/" `
    -Method POST `
    -Headers @{
        "Authorization" = "Token YOUR_TOKEN"
        "Content-Type" = "application/json"
    } `
    -Body $body

# Display the response
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

**Output**:
```
{
  "id":  "550e8400-e29b-41d4-a716-446655440000",
  "email":  "admin@hospital.com",
  "full_name":  "Dr. Ahmed Smith",
  ...rest of fields...
}
```

---

### Operation 2: View All Admins

#### Purpose
Get a list of all administrative staff members.

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Admin** section → **GET** → `/api/v1/admin/`
3. Click **"Try it out"**
4. You can set optional filters:
   - **search**: Find by name (e.g., "Ahmed")
   - **is_active**: true/false
   - **page**: Page number (default: 1)
   - **page_size**: Items per page (default: 20)
5. Click **Execute**

#### Step-by-Step via curl

```bash
# Get all admins
curl -X GET "http://localhost:8000/api/v1/admin/" ^
  -H "Authorization: Token YOUR_TOKEN"

# Search for specific admin
curl -X GET "http://localhost:8000/api/v1/admin/?search=Ahmed" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get only active admins
curl -X GET "http://localhost:8000/api/v1/admin/?is_active=true" ^
  -H "Authorization: Token YOUR_TOKEN"

# Pagination (page 2, 10 items per page)
curl -X GET "http://localhost:8000/api/v1/admin/?page=2&page_size=10" ^
  -H "Authorization: Token YOUR_TOKEN"
```

#### Response Example

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin1@hospital.com",
      "full_name": "Dr. Ahmed Smith",
      "employee_number": "ADM0001",
      "is_active": true
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "email": "admin2@hospital.com",
      "full_name": "Jane Wilson",
      "employee_number": "ADM0002",
      "is_active": true
    }
  ]
}
```

**Fields Explained**:
- `count`: Total number of admins
- `results`: Array of admin objects
- `next`: Link to next page (null if on last page)
- `previous`: Link to previous page (null if on first page)

---

### Operation 3: Get Admin Details

#### Purpose
View complete information about a specific admin.

#### Required
- `admin_id`: The unique ID from the admin object

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Admin** section → **GET** → `/api/v1/admin/{admin_id}/`
3. Enter the admin ID in the parameter
4. Click **Execute**

#### Step-by-Step via curl

```bash
# Replace ADMIN_ID with actual ID
curl -X GET "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

#### Response Example

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

### Operation 4: Update Admin Information

#### Purpose
Modify an admin's details (phone, department, email, name).

#### Fields You Can Update
- `email`
- `full_name`
- `phone`
- `department`
- `is_active` (true/false)

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Admin** section → **PATCH** → `/api/v1/admin/{admin_id}/`
3. Enter the admin ID
4. Fill in only the fields you want to change:
```json
{
  "phone": "555-0200",
  "department": "IT Department"
}
```
5. Click **Execute**

#### Step-by-Step via curl

```bash
# Update phone and department
curl -X PATCH "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"phone\":\"555-0200\",\"department\":\"IT\"}"

# Update only one field
curl -X PATCH "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"is_active\":false}"
```

---

### Operation 5: Delete/Deactivate Admin

#### Purpose
Remove or deactivate an admin account.

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Admin** section → **DELETE** → `/api/v1/admin/{admin_id}/`
3. Enter the admin ID
4. Click **Execute**
5. Response: `204 No Content` (success, no response body)

#### Step-by-Step via curl

```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/550e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

---

---

## 🧪 Lab Module

### What is the Lab Module?

The Lab Module manages **laboratory test orders and results**. It handles:
- Lab order creation
- Order status tracking
- Test result storage
- Patient sample management

**Key Characteristics**:
- Orders have status lifecycle: PENDING → IN_PROGRESS → COMPLETED
- Multiple tests per order
- Results stored per test
- Priority levels for urgent testing

---

### Lab Order Status Lifecycle

```
PENDING
  ↓ (Lab receives order)
IN_PROGRESS
  ↓ (Tests complete)
COMPLETED
  ↓
(Doctor retrieves results)
```

---

### Operation 1: Create Lab Order

#### Purpose
Doctor/Clinician orders laboratory tests for a patient.

#### Data Required
| Field | Type | Required | Example |
|-------|------|----------|---------|
| patient_id | UUID | ✅ Yes | 550e8400-e89b-41d4-a716-426614174000 |
| encounter_id | UUID | ✅ Yes | 660e8400-e89b-41d4-a716-426614174000 |
| test_codes | Array | ✅ Yes | ["CBC", "BMP"] |
| ordered_by | String | ✅ Yes | doctor@hospital.com |
| priority | String | ✅ Yes | NORMAL, URGENT, or STAT |
| notes | String | ❌ No | Routine checkup |

#### Available Test Codes

```
CBC  - Complete Blood Count
BMP  - Basic Metabolic Panel
LFT  - Liver Function Tests
RFT  - Renal Function Tests
UA   - Urinalysis
PT   - Prothrombin Time
PTT  - Partial Thromboplastin Time
```

#### Priority Levels

```
NORMAL  - Regular routine testing (default)
URGENT  - High priority, fast turnaround
STAT    - Immediate, emergency testing
```

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Lab** section → **POST** → `/api/v1/lab/`
3. Click **"Try it out"**
4. Enter request body:
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-426614174000",
  "encounter_id": "660e8400-e29b-41d4-a716-426614174000",
  "test_codes": ["CBC", "BMP", "LFT"],
  "ordered_by": "doctor@hospital.com",
  "priority": "NORMAL",
  "notes": "Routine checkup before discharge"
}
```
5. Click **Execute**

#### Step-by-Step via curl

```bash
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"patient_id\":\"550e8400-e29b-41d4-a716-426614174000\",\"encounter_id\":\"660e8400-e29b-41d4-a716-426614174000\",\"test_codes\":[\"CBC\",\"BMP\"],\"ordered_by\":\"doctor@hospital.com\",\"priority\":\"NORMAL\"}"
```

#### Response Example

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "patient_id": "550e8400-e29b-41d4-a716-426614174000",
  "encounter_id": "660e8400-e29b-41d4-a716-426614174000",
  "test_codes": ["CBC", "BMP", "LFT"],
  "ordered_by": "doctor@hospital.com",
  "priority": "NORMAL",
  "status": "PENDING",
  "notes": "Routine checkup before discharge",
  "is_active": true,
  "created_at": "2026-03-21T11:00:00Z"
}
```

**Key Points**:
- Order ID is needed for future operations
- Status automatically set to `PENDING`
- Tests are stored as array: `["CBC", "BMP", "LFT"]`

---

### Operation 2: View Lab Orders

#### Purpose
View list of lab orders with optional filtering.

#### Query Parameters (Optional)
- `patient_id` - Filter by patient UUID
- `status` - PENDING, IN_PROGRESS, or COMPLETED
- `priority` - NORMAL, URGENT, or STAT
- `page` - Page number
- `page_size` - Items per page

#### Step-by-Step via Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Find **Lab** section → **GET** → `/api/v1/lab/`
3. Set filters if desired
4. Click **Execute**

#### Step-by-Step via curl

```bash
# Get all orders
curl -X GET "http://localhost:8000/api/v1/lab/" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get pending orders
curl -X GET "http://localhost:8000/api/v1/lab/?status=PENDING" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get orders for specific patient
curl -X GET "http://localhost:8000/api/v1/lab/?patient_id=550e8400-e29b-41d4-a716-426614174000" ^
  -H "Authorization: Token YOUR_TOKEN"

# Get urgent orders
curl -X GET "http://localhost:8000/api/v1/lab/?priority=URGENT" ^
  -H "Authorization: Token YOUR_TOKEN"

# Paginate results
curl -X GET "http://localhost:8000/api/v1/lab/?page=1&page_size=5" ^
  -H "Authorization: Token YOUR_TOKEN"
```

#### Response Example

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
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440001",
      "patient_id": "550e8400-e29b-41d4-a716-426614174000",
      "test_codes": ["LFT"],
      "status": "IN_PROGRESS",
      "priority": "URGENT",
      "ordered_by": "doctor@hospital.com",
      "created_at": "2026-03-21T11:05:00Z"
    }
  ]
}
```

---

### Operation 3: Get Order Details

#### Purpose
View all information about a specific lab order.

#### Step-by-Step via curl

```bash
curl -X GET "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

#### Response Example

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "patient_id": "550e8400-e29b-41d4-a716-426614174000",
  "encounter_id": "660e8400-e89b-41d4-a716-426614174000",
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

### Operation 4: Update Order Status

#### Purpose
Change order status as tests progress through the workflow.

#### Valid Status Transitions

```
PENDING → IN_PROGRESS  (Lab starts processing)
IN_PROGRESS → COMPLETED  (All results entered)
```

#### Step-by-Step via curl

```bash
# Start processing (Mark as IN_PROGRESS)
curl -X PATCH "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"status\":\"IN_PROGRESS\"}"

# Mark complete (Mark as COMPLETED)
curl -X PATCH "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"status\":\"COMPLETED\"}"
```

---

### Operation 5: Add Test Results

#### Purpose
Enter test results as they come back from the lab.

#### Data Required
| Field | Type | Required | Example |
|-------|------|----------|---------|
| test_code | String | ✅ Yes | CBC |
| result_value | String | ✅ Yes | 7.5 |
| unit | String | ✅ Yes | 10^9/L |
| reference_range | String | ✅ Yes | 4.5-11.0 |
| performed_by | String | ✅ Yes | tech@hospital.com |

#### Step-by-Step via curl

```bash
# Add one test result
curl -X POST "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/add-result/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"test_code\":\"CBC\",\"result_value\":\"7.5\",\"unit\":\"10^9/L\",\"reference_range\":\"4.5-11.0\",\"performed_by\":\"tech@hospital.com\"}"

# Add second test result
curl -X POST "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/add-result/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -d "{\"test_code\":\"BMP\",\"result_value\":\"95\",\"unit\":\"mg/dL\",\"reference_range\":\"70-100\",\"performed_by\":\"tech@hospital.com\"}"
```

#### Response Example

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "test_code": "CBC",
  "result_value": "7.5",
  "unit": "10^9/L",
  "reference_range": "4.5-11.0",
  "status": "COMPLETED",
  "performed_by": "tech@hospital.com",
  "created_at": "2026-03-21T12:00:00Z"
}
```

---

### Operation 6: Get Order Results

#### Purpose
Retrieve all test results for a specific order.

#### Step-by-Step via curl

```bash
curl -X GET "http://localhost:8000/api/v1/lab/770e8400-e29b-41d4-a716-446655440000/results/" ^
  -H "Authorization: Token YOUR_TOKEN"
```

#### Response Example

```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440000",
    "test_code": "CBC",
    "result_value": "7.5",
    "unit": "10^9/L",
    "reference_range": "4.5-11.0",
    "status": "COMPLETED",
    "performed_by": "tech@hospital.com",
    "created_at": "2026-03-21T12:00:00Z"
  },
  {
    "id": "990e8400-e29b-41d4-a716-446655440001",
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

---

## 🔗 Integration Examples

### Example: Complete Lab Order Workflow

**Scenario**: Doctor orders tests, lab processes them, results come back

#### Step 1: Doctor Orders Tests
```bash
curl -X POST http://localhost:8000/api/v1/lab/ ^
  -H "Authorization: Token DOCTOR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\":\"patient-uuid\",\"encounter_id\":\"encounter-uuid\",\"test_codes\":[\"CBC\",\"BMP\"],\"ordered_by\":\"doctor@hospital.com\",\"priority\":\"NORMAL\"}"

# Response: Order created with id: 770e8400...
```

#### Step 2: Lab Sees New Order
```bash
curl -X GET "http://localhost:8000/api/v1/lab/?status=PENDING" ^
  -H "Authorization: Token LAB_TECH_TOKEN"

# Response: List includes the new order
```

#### Step 3: Lab Starts Processing
```bash
curl -X PATCH "http://localhost:8000/api/v1/lab/770e8400.../" ^
  -H "Authorization: Token LAB_TECH_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"IN_PROGRESS\"}"

# Response: Status changed to IN_PROGRESS
```

#### Step 4: Lab Adds Test Results (One per Test)
```bash
# Add CBC result
curl -X POST "http://localhost:8000/api/v1/lab/770e8400.../add-result/" ^
  -H "Authorization: Token LAB_TECH_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"test_code\":\"CBC\",\"result_value\":\"7.5\",\"unit\":\"10^9/L\",\"reference_range\":\"4.5-11.0\",\"performed_by\":\"tech@hospital.com\"}"

# Add BMP result
curl -X POST "http://localhost:8000/api/v1/lab/770e8400.../add-result/" ^
  -H "Authorization: Token LAB_TECH_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"test_code\":\"BMP\",\"result_value\":\"95\",\"unit\":\"mg/dL\",\"reference_range\":\"70-100\",\"performed_by\":\"tech@hospital.com\"}"
```

#### Step 5: Lab Marks Complete
```bash
curl -X PATCH "http://localhost:8000/api/v1/lab/770e8400.../" ^
  -H "Authorization: Token LAB_TECH_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"COMPLETED\"}"

# Response: Status changed to COMPLETED
```

#### Step 6: Doctor Retrieves Results
```bash
curl -X GET "http://localhost:8000/api/v1/lab/770e8400.../results/" ^
  -H "Authorization: Token DOCTOR_TOKEN"

# Response: Array of all test results with values
```

---

### Example: Admin Management Workflow

**Scenario**: Create and manage multiple admins

#### Step 1: Create Multiple Admins
```bash
# Create first admin
curl -X POST http://localhost:8000/api/v1/admin/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin1@hospital.com\",\"full_name\":\"Dr. Ahmed\"}"

# Create second admin
curl -X POST http://localhost:8000/api/v1/admin/ ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin2@hospital.com\",\"full_name\":\"Dr. Sarah\"}"
```

#### Step 2: List All Admins
```bash
curl -X GET "http://localhost:8000/api/v1/admin/" ^
  -H "Authorization: Token YOUR_TOKEN"

# Response: List of all admins with their details
```

#### Step 3: Update Admin Information
```bash
curl -X PATCH "http://localhost:8000/api/v1/admin/admin-id-1/" ^
  -H "Authorization: Token YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"phone\":\"555-0100\",\"department\":\"IT\"}"
```

#### Step 4: Search for Admins
```bash
curl -X GET "http://localhost:8000/api/v1/admin/?search=Ahmed" ^
  -H "Authorization: Token YOUR_TOKEN"

# Response: Only admins matching "Ahmed"
```

---

## ❌ Error Handling

### Common Errors & Solutions

#### Error: 400 Bad Request (Wrong Fields)
```
Response:
{
  "error": "missing required field: email"
}

Solution:
✓ Check request body has all required fields
✓ For Admin: email, full_name required
✓ For Lab: patient_id, encounter_id, test_codes, ordered_by, priority required
```

#### Error: 401 Unauthorized
```
Response:
{
  "detail": "Authentication credentials were not provided."
}

Solution:
✓ Add Authorization header with valid token
✓ Format: "Authorization: Token abc123..."
✓ Get token from login endpoint first
```

#### Error: 404 Not Found
```
Response:
{
  "detail": "Not found."
}

Solution:
✓ Check the admin_id or order_id is correct
✓ ID should be a valid UUID format
✓ Verify object exists in database
```

#### Error: 409 Conflict (Email Already Exists)
```
Response:
{
  "error": "This email already exists"
}

Solution:
✓ Use a different email address
✓ Check if admin/user already registered with that email
```

#### Error: 422 Unprocessable Entity (Invalid Data)
```
Response:
{
  "error": "Status transition not allowed"
}

Solution for Lab:
✓ PENDING can only go to IN_PROGRESS
✓ IN_PROGRESS can only go to COMPLETED
✓ Cannot go backwards (COMPLETED → PENDING not allowed)
```

---

## ✅ Verification Checklist

Before using in production:

**Admin Module**
- [ ] Can create new admin
- [ ] Can view all admins
- [ ] Can search admins by name
- [ ] Can update admin details
- [ ] Can deactivate admin

**Lab Module**
- [ ] Can create lab order
- [ ] Can view pending orders
- [ ] Can transition: PENDING → IN_PROGRESS
- [ ] Can add test results
- [ ] Can transition: IN_PROGRESS → COMPLETED
- [ ] Can retrieve all results for an order

---

**End of Operations Guide**

For more information, see:
- COMPLETE_GUIDE.md - Full system documentation
- API_TESTING.md - Additional testing methods
- GETTING_STARTED.md - 5-minute quick start

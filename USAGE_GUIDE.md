
# 🏥 HOSPITAL MANAGEMENT SYSTEM - USAGE GUIDE

## ✅ System Status
- **Server:** Running on http://localhost:8000
- **Database:** SQLite (initialized with all 40 models)
- **Admin User:** admin@hospital.com / Admin@12345
- **Modules:** Lab, Billing, Admin

---

## 📋 TABLE OF CONTENTS
1. [Access Points](#access-points)
2. [Admin Panel Walkthrough](#admin-panel-walkthrough)
3. [Lab Module Usage](#lab-module-usage)
4. [Billing Module Usage](#billing-module-usage)
5. [Admin Module Usage](#admin-module-usage)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 ACCESS POINTS

### Option 1: Admin Panel (Web Interface)
```
URL: http://localhost:8000/admin/
Email: admin@hospital.com
Password: Admin@12345
```
✓ Manage everything visually through the web interface

### Option 2: Django Shell (Command Line)
```bash
python manage.py shell
```
✓ Create, update, delete records using Python

### Option 3: Run Test Scripts
```bash
python run_system_test.py     # Test all modules
python show_db.py             # View all database data
python check_users.py         # View all users
```

---

## 💻 ADMIN PANEL WALKTHROUGH

### Step 1: Login to Admin Panel
1. Go to: **http://localhost:8000/admin/**
2. Login with:
   - **Email:** admin@hospital.com
   - **Password:** Admin@12345
3. Click "Sign In"

### Step 2: Dashboard Overview
You'll see the admin dashboard with:
- **Left Sidebar:** All available modules
- **Main Area:** Quick status and actions
- **Top Right:** User profile & settings

### Step 3: Navigate to Modules
In the left sidebar, click:
- **Lab** → Manage lab orders, specimens, results
- **Billing** → Manage invoices, payments, accounts
- **Admin** → Manage departments, wards, beds

---

## 🧪 LAB MODULE USAGE

### Via Admin Panel

**Create a Lab Order:**
1. Go to Admin Panel
2. Click **Lab** → **Lab Orders**
3. Click **Add Lab Order** (blue button)
4. Fill in:
   - **Patient ID:** (any ID, e.g., patient-001)
   - **Encounter ID:** (any ID, e.g., encounter-001)
   - **Test Codes:** (e.g., CBC, LFT, RBS - comma separated)
   - **Ordered By:** (e.g., Dr. Ahmed)
   - **Status:** PENDING
   - **Priority:** ROUTINE
   - **Notes:** (optional details)
5. Click **Save**

**View Lab Orders:**
1. Go to Admin Panel
2. Click **Lab** → **Lab Orders**
3. See all orders in the list
4. Click any order to edit or view details

**Track Lab Workflow:**
1. Order created → Status: PENDING
2. Specimen collected → Create Specimen record
3. Tests run → Create Result record
4. Results verified → Create Report
5. Report released → Complete

### Via Django Shell

```python
from apps.lab.infrastructure.orm_models import LabOrder
from uuid import uuid4

# Create lab order
order = LabOrder.objects.create(
    patient_id=uuid4(),
    encounter_id=uuid4(),
    test_codes=["CBC", "LFT"],
    ordered_by="Dr. Ahmed",
    status="PENDING",
    priority="ROUTINE"
)

# View all orders
LabOrder.objects.all()

# Get specific order
order = LabOrder.objects.get(id="<order-id>")

# Update status
order.status = "IN_PROGRESS"
order.save()
```

---

## 💳 BILLING MODULE USAGE

### Via Admin Panel

**Create Patient Account:**
1. Go to Admin Panel
2. Click **Billing** → **Patient Accounts**
3. Click **Add Patient Account**
4. Fill in:
   - **Patient ID:** (any ID)
   - **Account Number:** (auto-generated or enter custom)
   - **Status:** ACTIVE
   - **Insurance Info:** (JSON, e.g., {"provider": "Insurance Name"})
   - **Preferred Payment Method:** CASH / CARD / INSURANCE
5. Click **Save**

**Create Invoice:**
1. Go to **Billing** → **Invoices**
2. Click **Add Invoice**
3. Fill in:
   - **Account:** (select patient account)
   - **Invoice Number:** (auto-generated)
   - **Invoice Date:** (today's date)
   - **Due Date:** (30 days from today)
   - **Subtotal:** (e.g., 500.00)
   - **Tax:** (e.g., 0.00)
   - **Discount:** (e.g., 0.00)
   - **Total Amount:** (calculated)
   - **Status:** DRAFT
   - **Created By:** (your name)
4. Click **Save**

**Create Payment:**
1. Go to **Billing** → **Payments**
2. Click **Add Payment**
3. Fill in:
   - **Invoice:** (select invoice)
   - **Payment Date:** (today)
   - **Amount Paid:** (payment amount)
   - **Payment Method:** CASH / CARD / INSURANCE
   - **Reference:** (optional document number)
3. Click **Save**

**Track Financial Workflow:**
1. Account created → Status: ACTIVE
2. Invoice issued → Status: DRAFT
3. Invoice sent → Status: SENT
4. Payment received → Status: PARTIALLY_PAID or FULLY_PAID
5. Year-end → Create reports and archive

### Via Django Shell

```python
from apps.billing.infrastructure.orm_billing_models import PatientAccount, Invoice, Payment
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal

# Create patient account
account = PatientAccount.objects.create(
    patient_id=uuid4(),
    account_number=f"ACC-{uuid4().hex[:8]}",
    status="active",
    total_balance=Decimal('0.00')
)

# Create invoice
today = datetime.now().date()
invoice = Invoice.objects.create(
    account=account,
    invoice_number=f"INV-{uuid4().hex[:6]}",
    invoice_date=today,
    due_date=today + timedelta(days=30),
    subtotal=Decimal('500.00'),
    total_amount=Decimal('500.00'),
    remaining_balance=Decimal('500.00'),
    created_by="System",
    status="draft"
)

# Create payment
payment = Payment.objects.create(
    invoice=invoice,
    payment_date=today,
    amount_paid=Decimal('500.00'),
    payment_method="CASH"
)

# View all accounts
PatientAccount.objects.all()
```

---

## 👨‍💼 ADMIN MODULE USAGE

### Via Admin Panel

**Create Department:**
1. Go to Admin Panel
2. Click **Admin** → **Departments**
3. Click **Add Department**
4. Fill in:
   - **Name:** (e.g., Cardiology, Surgery)
   - **Code:** (e.g., CARD-001, SURG-001)
   - **Description:** (details about department)
5. Click **Save**

**Create Ward:**
1. Go to **Admin** → **Wards**
2. Click **Add Ward**
3. Fill in:
   - **Name:** (e.g., Cardiac Ward)
   - **Department:** (select from dropdown)
   - **Capacity:** (number of beds)
4. Click **Save**

**Create Bed:**
1. Go to **Admin** → **Beds**
2. Click **Add Bed**
3. Fill in:
   - **Bed Number:** (e.g., BED-001)
   - **Ward:** (select from dropdown)
   - **Type:** (ICU, General, VIP, etc.)
   - **Status:** AVAILABLE / OCCUPIED / MAINTENANCE
4. Click **Save**

### Via Django Shell

```python
from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed
from uuid import uuid4

# Create department
dept = Department.objects.create(
    name="Cardiology",
    code="CARD-001",
    description="Heart and cardiovascular care"
)

# Create ward
ward = Ward.objects.create(
    name="Cardiac Ward",
    department=dept,
    capacity=20
)

# Create bed
bed = Bed.objects.create(
    bed_number="BED-001",
    ward=ward,
    bed_type="ICU",
    status="available"
)

# View all departments
Department.objects.all()
```

---

## 🔄 COMMON WORKFLOWS

### Workflow 1: Patient Lab Testing
```
1. Doctor orders lab tests
   → Create LabOrder in Lab module
   
2. Lab techs collect specimen
   → Create Specimen record
   
3. Tests are analyzed
   → Create LabResult record
   
4. Results reviewed and verified
   → Update status to VERIFIED
   
5. Report generated
   → Create LabReport
   
6. Report sent to doctor
   → Doctor reviews results
```

**How to execute in system:**
```bash
# Login to admin panel
# Lab → Lab Orders → Add Lab Order
# Lab → Specimens → Add Specimen
# Lab → Lab Results → Add Result
# Lab → Lab Reports → Add Report
```

### Workflow 2: Patient Billing
```
1. Patient admitted to hospital
   → Create PatientAccount
   
2. Services provided (lab, room, etc)
   → Create Invoice with line items
   
3. Invoice finalized and sent
   → Update status to SENT
   
4. Patient makes payment
   → Create Payment record
   
5. Invoice marked as paid
   → Update status to FULLY_PAID
```

**How to execute in system:**
```bash
# Login to admin panel
# Billing → Patient Accounts → Add Account
# Billing → Invoices → Add Invoice
# Billing → Invoices → Edit → Send
# Billing → Payments → Add Payment
```

### Workflow 3: Hospital Administration
```
1. Set up hospital structure
   → Create Departments
   → Create Wards
   → Create Beds
   
2. Assign staff to departments
   → Add department heads
   
3. Manage resources
   → Track bed availability
   → Monitor capacity
```

**How to execute in system:**
```bash
# Login to admin panel
# Admin → Departments → Add Department
# Admin → Wards → Add Ward
# Admin → Beds → Add Bed
```

---

## 📊 RUNNING TESTS & VIEWING DATA

### Test All Modules
```bash
python run_system_test.py
```
Output: Creates sample data and shows test results

### View All Database Records
```bash
python show_db.py
```
Output: Shows count of all tables and sample records

### Check All Users
```bash
python check_users.py
```
Output: Lists all registered users in system

### Django Shell for Custom Queries
```bash
python manage.py shell

# Then type Python commands:
from apps.lab.infrastructure.orm_models import LabOrder
LabOrder.objects.all()  # Get all orders
LabOrder.objects.count()  # Count orders
LabOrder.objects.filter(status="PENDING")  # Filter by status
```

---

## ⚠️ TROUBLESHOOTING

### Problem 1: Can't login to admin panel
**Solution:**
1. Check credentials: admin@hospital.com / Admin@12345
2. Verify server is running: http://localhost:8000 should show Django page
3. Check user exists:
   ```bash
   python check_users.py
   ```

### Problem 2: Getting "Object does not exist" error
**Solution:**
1. Make sure related object exists before creating dependent object
2. For example: Create PatientAccount before creating Invoice

### Problem 3: Database locked or connection error
**Solution:**
1. Restart server:
   ```bash
   # Kill current server
   # Then restart: python manage.py runserver 0.0.0.0:8000
   ```

### Problem 4: Changes not appearing in admin panel
**Solution:**
1. Refresh the page (Ctrl+F5)
2. Clear browser cache
3. Make sure you clicked "Save" button

### Problem 5: "Module not found" error
**Solution:**
1. Make sure you're in correct directory:
   ```bash
   cd d:\SEMESTER 7\Graduation Project\vh_django_final_1\vh_django_final_1\vh_django
   ```
2. Verify migrations are applied:
   ```bash
   python manage.py migrate
   ```

---

## 🔑 QUICK REFERENCE

| Task | Steps |
|------|-------|
| **Add Lab Order** | Admin Panel → Lab → Lab Orders → Add |
| **Create Invoice** | Admin Panel → Billing → Invoices → Add |
| **Process Payment** | Admin Panel → Billing → Payments → Add |
| **Create Department** | Admin Panel → Admin → Departments → Add |
| **View All Data** | `python show_db.py` |
| **Test System** | `python run_system_test.py` |
| **Django Shell** | `python manage.py shell` |

---

## ✅ CHECKLIST FOR FIRST-TIME USE

- [ ] Server running: http://localhost:8000
- [ ] Can login to admin: admin@hospital.com / Admin@12345
- [ ] Database initialized (run `python manage.py migrate`)
- [ ] Test data created (run `python run_system_test.py`)
- [ ] Can see Lab Orders in admin panel
- [ ] Can see Patient Accounts in admin panel
- [ ] Can see Departments in admin panel
- [ ] System ready for use!

---

## 📞 SUPPORT

For issues or questions:
1. Check troubleshooting section above
2. Run `python show_db.py` to verify data
3. Check error messages carefully
4. Restart server if needed
5. Verify database: `python manage.py check`

**System is ready to use!** 🚀


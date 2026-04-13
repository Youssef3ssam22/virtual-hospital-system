
# 🏥 HOSPITAL SYSTEM - COMPLETE USAGE STEPS

## ✅ SYSTEM CHECK RESULTS
```
System check identified no issues (0 silenced).
✓ All 3 modules verified: Lab, Billing, Admin
✓ Database: Initialized
✓ Server: Ready
✓ No errors or warnings detected
```

---

## 🚀 STEP 0: START THE SERVER

If not already running:
```bash
python manage.py runserver 0.0.0.0:8000
```

✓ Server will start at: **http://localhost:8000**

Verify it's running:
```bash
# In another terminal
python -c "import requests; print('✓ Server OK' if requests.get('http://localhost:8000').status_code else 'X Server Error')"
```

---

## 🔐 STEP 1: LOGIN TO ADMIN PANEL

### Method 1: Web Browser (Easiest)

1. **Open browser:**
   ```
   http://localhost:8000/admin/
   ```

2. **Enter credentials:**
   - Email: `admin@hospital.com`
   - Password: `Admin@12345`

3. **Click "Sign In"**

4. **You should see dashboard with 3 main sections:**
   - Lab
   - Billing  
   - Admin

---

## 🧪 STEP 2A: LAB MODULE - CREATE LAB ORDER

### Via Admin Panel (Recommended)

**Step 1:** Go to Dashboard → **Lab** → **Lab Orders**

**Step 2:** Click blue **"Add Lab Order"** button

**Step 3:** Fill in the form:
```
Patient ID:      patient-001  (any ID)
Encounter ID:    encounter-001  (any ID)
Test Codes:      CBC, LFT, RBS  (comma-separated)
Ordered By:      Dr. Ahmed Hassan  (doctor name)
Status:          PENDING  (dropdown)
Priority:        ROUTINE  (dropdown)
Notes:           Regular checkup  (optional)
```

**Step 4:** Click **"Save"** (green button)

**✅ Lab Order Created!**

### Via Django Shell (For Advanced Users)

```bash
python manage.py shell
```

Then type:
```python
from apps.lab.infrastructure.orm_models import LabOrder
from uuid import uuid4

order = LabOrder.objects.create(
    patient_id=uuid4(),
    encounter_id=uuid4(),
    test_codes=["CBC", "LFT", "RBS"],
    ordered_by="Dr. Ahmed",
    status="PENDING",
    priority="ROUTINE",
    notes="Regular checkup"
)

print(f"✓ Lab Order Created: {order.id}")

# View all orders
LabOrder.objects.all()

# View single order
LabOrder.objects.get(id=order.id)

exit()
```

---

## 🧪 STEP 2B: LAB MODULE - VIEW & MANAGE ORDERS

### View All Lab Orders

1. Go to Admin → **Lab** → **Lab Orders**
2. See list of all orders with:
   - Order ID
   - Patient ID
   - Status
   - Priority
   - Created date

### Edit Lab Order

1. Click on any order in the list
2. Edit fields as needed
3. Click **"Save"** to update

### Track Lab Workflow

**Lab workflow steps:**
```
1. Order Created
   └─ Status: PENDING

2. Specimen Collected
   └─ Go to Lab → Specimens
   └─ Add Specimen

3. Tests Run
   └─ Go to Lab → Lab Results
   └─ Add Result

4. Results Verified
   └─ Update status to COMPLETED

5. Report Generated
   └─ Go to Lab → Lab Reports
   └─ Add Report

6. Report Sent to Doctor
   └─ Mark as COMPLETED
```

**In Admin Panel:**
```
Lab → Lab Orders → (Select order) → View status
Lab → Specimens → Add Specimen (when collected)
Lab → Lab Results → Add Result (when analyzed)
Lab → Lab Reports → Add Report (final report)
```

---

## 💳 STEP 3A: BILLING MODULE - CREATE PATIENT ACCOUNT

### Via Admin Panel

**Step 1:** Go to Dashboard → **Billing** → **Patient Accounts**

**Step 2:** Click **"Add Patient Account"** button

**Step 3:** Fill in form:
```
Patient ID:              patient-123  (unique)
Account Number:          ACC-2024-001  (reference)
Status:                  ACTIVE  (dropdown)
Preferred Payment Method: CASH  (dropdown)
Insurance Info:          (JSON - optional)
                         {"provider": "Local Insurance"}
```

**Step 4:** Click **"Save"**

**✅ Patient Account Created!**

---

## 💳 STEP 3B: BILLING MODULE - CREATE INVOICE

### Via Admin Panel

**Step 1:** Go to Dashboard → **Billing** → **Invoices**

**Step 2:** Click **"Add Invoice"** button

**Step 3:** Fill in form:
```
Account:           (Select from dropdown - choose patient account)
Invoice Number:    INV-2024-001  (unique)
Invoice Date:      2024-03-23  (today)
Due Date:          2024-04-22  (30 days later)
Subtotal:          500.00
Tax:               0.00
Discount:          0.00
Total Amount:      500.00
Status:            DRAFT  (dropdown)
Created By:        Admin  (your name)
```

**Step 4:** Click **"Save"**

**✅ Invoice Created!**

---

## 💳 STEP 3C: BILLING MODULE - RECORD PAYMENT

### Via Admin Panel

**Step 1:** Go to Dashboard → **Billing** → **Payments**

**Step 2:** Click **"Add Payment"** button

**Step 3:** Fill in form:
```
Invoice:           (Select from dropdown)
Payment Date:      2024-03-23  (today)
Amount Paid:       500.00  (payment amount)
Payment Method:    CASH  (dropdown)
Reference:        (optional - check/receipt number)
```

**Step 4:** Click **"Save"**

**✅ Payment Recorded!**

### View Payment Status

Go to **Billing → Invoices** → Click invoice → See:
```
Total Amount:      500.00
Paid Amount:       500.00
Remaining Balance: 0.00
Status:            FULLY_PAID
```

---

## 👨‍💼 STEP 4A: ADMIN MODULE - CREATE DEPARTMENT

### Via Admin Panel

**Step 1:** Go to Dashboard → **Admin** → **Departments**

**Step 2:** Click **"Add Department"** button

**Step 3:** Fill in form:
```
Name:               Cardiology  (department name)
Code:               CARD-001  (unique code)
Description:       Heart and cardiovascular diseases
Status:             ACTIVE  (optional)
```

**Step 4:** Click **"Save"**

**✅ Department Created!**

---

## 👨‍💼 STEP 4B: ADMIN MODULE - CREATE WARD

### Via Admin Panel

**Step 1:** Go to Dashboard → **Admin** → **Wards**

**Step 2:** Click **"Add Ward"** button

**Step 3:** Fill in form:
```
Name:              Cardiac Ward  (ward name)
Department:        (Select Cardiology from dropdown)
Capacity:          20  (number of beds)
Status:            ACTIVE  (optional)
```

**Step 4:** Click **"Save"**

**✅ Ward Created!**

---

## 👨‍💼 STEP 4C: ADMIN MODULE - CREATE BED

### Via Admin Panel

**Step 1:** Go to Dashboard → **Admin** → **Beds**

**Step 2:** Click **"Add Bed"** button

**Step 3:** Fill in form:
```
Bed Number:        BED-001  (unique identifier)
Ward:              (Select Cardiac Ward from dropdown)
Bed Type:          ICU  (or General, VIP)
Status:            AVAILABLE  (dropdown)
```

**Step 4:** Click **"Save"**

**✅ Bed Created!**

---

## 📊 STEP 5: VIEW ALL DATA

### Option 1: Admin Panel Dashboard
Just navigate through the sidebar and click any section

### Option 2: Run Test Script
```bash
python show_db.py
```
Shows:
- Total count of each table
- Sample records
- Module status

### Option 3: Django Shell
```bash
python manage.py shell

# Lab data
from apps.lab.infrastructure.orm_models import LabOrder
LabOrder.objects.count()  # How many orders
LabOrder.objects.all()     # All orders

# Billing data
from apps.billing.infrastructure.orm_billing_models import PatientAccount, Invoice
PatientAccount.objects.count()
Invoice.objects.count()

# Admin data
from apps.admin.infrastructure.orm_admin_models import Department
Department.objects.count()

exit()
```

---

## 🔄 STEP 6: COMPLETE WORKFLOW EXAMPLE

### Scenario: Patient comes for lab tests, gets billed

**STEP 1: Create Patient Account**
```
Billing → Patient Accounts → Add
   Patient ID: PAT-2024-001
   Account: ACC-001
→ Save
```

**STEP 2: Doctor Orders Lab Tests**
```
Lab → Lab Orders → Add
   Patient: PAT-2024-001
   Tests: CBC, LFT
   Ordered By: Dr. Ahmed
   Status: PENDING
→ Save
```

**STEP 3: Lab Collects Specimen**
```
Lab → Specimens → Add
   Patient: PAT-2024-001
   Type: Blood
   Collection Time: Now
   Status: Collected
→ Save
```

**STEP 4: Results Analyzed**
```
Lab → Lab Results → Add
   Specimen: (select specimen)
   Value: (test results)
   Status: Verified
→ Save
```

**STEP 5: Create Invoice**
```
Billing → Invoices → Add
   Account: ACC-001
   Amount: 500.00 (lab + services)
   Due Date: 30 days
   Status: DRAFT
→ Save
```

**STEP 6: Process Payment**
```
Billing → Payments → Add
   Invoice: INV-001
   Amount: 500.00
   Method: CASH
→ Save
```

**✅ Complete Workflow Done!**

---

## ⚡ QUICK COMMAND REFERENCE

| Task | Command |
|------|---------|
| **Start Server** | `python manage.py runserver 0.0.0.0:8000` |
| **Check System** | `python manage.py check` |
| **View Data** | `python show_db.py` |
| **Run Tests** | `python run_system_test.py` |
| **Django Shell** | `python manage.py shell` |
| **Migrations** | `python manage.py migrate` |
| **Access Admin** | http://localhost:8000/admin/ |

---

## 🗂️ MODULE QUICK ACCESS

### Lab Module
- **Lab Orders:** Order tests for patients
- **Specimens:** Track physical samples
- **Lab Results:** Enter test results
- **Lab Reports:** Generate final reports

### Billing Module
- **Patient Accounts:** Patient billing accounts
- **Invoices:** Create bills for services
- **Payments:** Record payment received
- **Insurance Claims:** Track insurance claims
- **Financial Timeline:** View payment history

### Admin Module
- **Departments:** Hospital departments
- **Wards:** Hospital wards/units
- **Beds:** Bed management
- **System Config:** Hospital settings

---

## ✅ USAGE CHECKLIST

### Day 1 - Setup
- [ ] Server running: http://localhost:8000
- [ ] Can login to admin: admin@hospital.com / Admin@12345
- [ ] Can see all 3 modules in left sidebar
- [ ] Database check: `python manage.py check` ✓

### Day 2 - Lab Module
- [ ] Create a lab order
- [ ] View all lab orders
- [ ] Add a specimen
- [ ] Add lab result
- [ ] Generate report

### Day 3 - Billing Module
- [ ] Create patient account
- [ ] Create invoice
- [ ] Record payment
- [ ] View payment status

### Day 4 - Admin Module
- [ ] Create department
- [ ] Create ward
- [ ] Create beds
- [ ] Assign beds to wards

### Day 5 - Full Test
- [ ] Run complete workflow (all 3 modules)
- [ ] `python test_modules.py`
- [ ] All features working ✓

---

## 🎯 COMMON ISSUES & SOLUTIONS

### Issue: Can't login
**Solution:**
- Check email: `admin@hospital.com` (with @)
- Check password: `Admin@12345` (case-sensitive)
- Restart server

### Issue: Data not saving
**Solution:**
- Make sure you clicked "Save" button
- Check for red error messages
- Verify all required fields are filled

### Issue: Can't see modules
**Solution:**
- Refresh page (Ctrl+F5)
- Clear browser cache
- Logout and login again

### Issue: Server not responding
**Solution:**
```bash
# Restart server
python manage.py runserver 0.0.0.0:8000
```

---

## 📞 SUPPORT COMMANDS

```bash
# Check everything
python manage.py check

# View all data
python show_db.py

# Run complete test
python run_system_test.py

# Check users
python check_users.py

# View logs
# Check logs/ folder
```

---

## 🎓 SUMMARY

**Your system has 3 fully operational modules:**

```
✓ Lab Module      - Create & track lab orders
✓ Billing Module  - Invoice & payment management  
✓ Admin Module    - Hospital resource management
```

**All connected with:**
```
✓ Authentication  - Secure login
✓ RBAC           - Role-based access control
✓ Validation     - Data integrity checks
✓ Audit Logging  - Track all operations
```

**System Status: 🟢 READY TO USE**

Now pick any task from the steps above and start using the system! 🚀


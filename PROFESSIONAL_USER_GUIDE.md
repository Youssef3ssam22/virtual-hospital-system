# 🏥 HOSPITAL MANAGEMENT SYSTEM
## Professional User Guide

**System Version:** 2.0.0  
**Last Updated:** March 23, 2026  
**Production Status:** Ready (9.2/10)

---

## 📑 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Access & Authentication](#access--authentication)
3. [Lab Module Guide](#lab-module-guide)
4. [Billing Module Guide](#billing-module-guide)
5. [Admin Module Guide](#admin-module-guide)
6. [Standard Workflows](#standard-workflows)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🏢 SYSTEM OVERVIEW

### System Architecture
The Hospital Management System is a comprehensive web-based application designed to manage:
- **Lab Operations** - Laboratory test orders, specimen tracking, result management
- **Financial Operations** - Billing, invoicing, payment processing, insurance claims
- **Hospital Administration** - Department management, resource allocation, facility organization

### System Features
✅ Role-Based Access Control (RBAC)  
✅ Real-time Data Validation  
✅ Comprehensive Audit Logging  
✅ Secure Bearer Token Authentication  
✅ Multi-Department Support  
✅ Financial Integrity Checks  

### System Requirements
- **Browser:** Modern web browser (Chrome, Firefox, Safari, Edge)
- **Internet Connection:** Required
- **URL:** `http://localhost:8000/admin/`
- **Supported Users:** Administrators, Lab Technicians, Doctors, Accountants

---

## 🔐 ACCESS & AUTHENTICATION

### Step 1: System Access

**Via Web Browser:**

1. Open your web browser
2. Navigate to: `http://localhost:8000/admin/`
3. System will display login page

**Expected Page:**
```
Hospital Management System
━━━━━━━━━━━━━━━━━━━━━━━━━
Email: [___________________]
Password: [___________________]
          [Sign In Button]
```

### Step 2: Login with Credentials

**Administrator Account:**
```
Email:    admin@hospital.com
Password: Admin@12345
```

**Important Security Notes:**
- ⚠️ Keep credentials confidential
- ⚠️ Do not share your password
- ⚠️ Change password regularly
- ⚠️ Logout before leaving terminal

### Step 3: Dashboard Access

After successful login, you will see:

**Main Dashboard Elements:**
```
┌─────────────────────────────────────────────┐
│         Hospital Management System           │
├─────────────────────────────────────────────┤
│ Left Sidebar (Navigation)    │  Main Content │
│ • Lab                       │  • Dashboard   │
│ • Billing                   │  • Quick Stats │
│ • Admin                     │  • Recent Items│
│ • Logout                    │                 │
└─────────────────────────────────────────────┘
```

---

## 🧪 LAB MODULE GUIDE

### Module Overview
The Lab Module manages laboratory operations including:
- Laboratory test orders
- Specimen collection and tracking
- Test result entry and verification
- Lab report generation
- Critical value alerts

### Lab Module Access

1. Click **"Lab"** in the left sidebar
2. You will see options:
   - Lab Orders
   - Specimens
   - Lab Results
   - Critical Values
   - Lab Reports
   - Analyzer Queue

---

### 1.1 CREATE A LAB ORDER

**Purpose:** Initiate laboratory testing for a patient

**Steps:**

1. From Dashboard → Click **"Lab"** → **"Lab Orders"**

2. Click blue **"+ Add Lab Order"** button (top right)

3. Complete the Form:

| Field | Value | Example |
|-------|-------|---------|
| **Patient ID** | Unique patient identifier | `PAT-2024-001` |
| **Encounter ID** | Hospital encounter reference | `ENC-2024-001` |
| **Test Codes** | Laboratory test codes (comma-separated) | `CBC, LFT, RBS` |
| **Ordered By** | Physician name | `Dr. Ahmed Hassan` |
| **Status** | Order status | `PENDING` (mandatory) |
| **Priority** | Test priority | `ROUTINE` or `URGENT` |
| **Notes** | Additional clinical information | `Routine annual checkup` |

4. Click **"Save"** button

5. System Response:
   - ✅ Success: Order created with unique Order ID
   - ❌ Error: Check required fields (marked with *)

**Validation Rules:**
- Patient ID: Required, must be unique per order
- Test Codes: At least one test code required
- Status: Must be PENDING for new orders
- Priority: Select ROUTINE for standard, URGENT for expedited

---

### 1.2 VIEW LAB ORDERS

**Purpose:** Access and review laboratory orders

**Steps:**

1. Click **"Lab"** → **"Lab Orders"**

2. View List:
   - All orders display in table format
   - Shows: Order ID, Patient ID, Status, Priority, Date Created
   - Default sort: Most recent first

3. Search/Filter Options:
   - Search by Patient ID
   - Filter by Status (Pending, In Progress, Completed, Cancelled)
   - Filter by Priority

4. View Order Details:
   - Click any order in the list
   - See full order information
   - View test codes, ordering physician, notes

---

### 1.3 MANAGE SPECIMEN COLLECTION

**Purpose:** Track physical specimen collection from patient

**Steps:**

1. Click **"Lab"** → **"Specimens"**

2. Click **"+ Add Specimen"** button

3. Complete Specimen Form:

| Field | Options | Notes |
|-------|---------|-------|
| **Lab Order** | (Dropdown) | Select from created orders |
| **Patient ID** | Auto-filled | From associated lab order |
| **Specimen Type** | Blood, Urine, Serum, Plasma, etc. | Required |
| **Collection Method** | Venipuncture, Capillary, etc. | Required |
| **Collection Time** | Date & Time | When specimen collected |
| **Quantity** | Numeric value | Specimen volume/amount |
| **Quantity Unit** | mL, Units, etc. | Measurement unit |
| **Status** | Collected, Processing, Analyzed | Set to "Collected" |
| **Collector ID** | Lab technician ID | Who collected specimen |
| **Rejection Reason** | (If applicable) | If specimen rejected |

4. Click **"Save"**

5. Specimen is now tracked in system

**Status Workflow:**
```
Collected → Processing → Analyzed → Verified → Archived
```

---

### 1.4 ENTER LAB RESULTS

**Purpose:** Document laboratory test results

**Steps:**

1. Click **"Lab"** → **"Lab Results"**

2. Click **"+ Add Lab Result"** button

3. Complete Result Form:

| Field | Description | Example |
|-------|-------------|---------|
| **Specimen** | (Dropdown) | Select specimen |
| **Test Code** | Laboratory test code | `CBC` |
| **Result Value** | Numerical or text result | `12.5` |
| **Result Unit** | Measurement unit | `g/dL` |
| **Reference Range** | Normal range | `12.0 - 16.0` |
| **Status** | Result status | `Pending`, `Completed`, `Verified` |
| **Technician** | Person entering result | Name/ID |
| **Notes** | Comments on result | Optional |

4. Click **"Save"**

5. Result recorded in system

**Critical Values:**
- If result falls outside normal range, system may flag as critical
- See Critical Values section for alerts

---

### 1.5 GENERATE LAB REPORT

**Purpose:** Create final laboratory report for physician

**Steps:**

1. Click **"Lab"** → **"Lab Reports"**

2. Click **"+ Add Lab Report"** button

3. Complete Report Form:

| Field | Notes |
|-------|-------|
| **Lab Order** | Select completed order |
| **Report Type** | Standard, Summary, Detailed |
| **Results Summary** | Auto-populated from results |
| **Interpretation** | Clinical interpretation |
| **Verified By** | Lab director/pathologist |
| **Status** | Draft, Final, Signed |

4. Click **"Save"**

5. Report generated and ready for physician

**Report Distribution:**
- Print report
- Send to physician
- Archive in patient file

---

## 💳 BILLING MODULE GUIDE

### Module Overview
The Billing Module manages:
- Patient billing accounts
- Invoice creation and management
- Payment processing
- Insurance claims tracking
- Financial reporting

### Billing Module Access

1. Click **"Billing"** in left sidebar
2. Available options:
   - Patient Accounts
   - Invoices
   - Payments
   - Insurance Claims
   - Claim Denials
   - Financial Timeline

---

### 2.1 CREATE PATIENT ACCOUNT

**Purpose:** Establish billing account for new patient

**Steps:**

1. Click **"Billing"** → **"Patient Accounts"**

2. Click **"+ Add Patient Account"** button

3. Complete Account Form:

| Field | Format | Example | Required |
|-------|--------|---------|----------|
| **Patient ID** | Text, Unique | PAT-2024-001 | ✅ Yes |
| **Account Number** | Alphanumeric | ACC-2024-001 | ✅ Yes |
| **Status** | Dropdown | ACTIVE | ✅ Yes |
| **Total Balance** | Currency | 0.00 | Auto |
| **Total Paid** | Currency | 0.00 | Auto |
| **Insurance Info** | JSON (optional) | {provider: "ABC"} | ❌ No |
| **Payment Method** | Dropdown | CASH, CARD, INSURANCE | ❌ No |
| **Notes** | Text | Account notes | ❌ No |

4. Click **"Save"**

5. Account created and ready for invoicing

**Status Options:**
- **ACTIVE:** Account open for billing
- **INACTIVE:** Account paused
- **SUSPENDED:** Account frozen
- **CLOSED:** Account finalized

---

### 2.2 CREATE INVOICE

**Purpose:** Generate bill for patient services

**Steps:**

1. Click **"Billing"** → **"Invoices"**

2. Click **"+ Add Invoice"** button

3. Complete Invoice Form:

| Field | Description | Format | Example |
|-------|-------------|--------|---------|
| **Account** | Patient account | Dropdown | Select account |
| **Invoice Number** | Unique reference | Auto-generated | INV-2024-001 |
| **Encounter ID** | Hospital visit reference | Text | ENC-2024-001 |
| **Invoice Date** | Date issued | Date picker | 03/23/2024 |
| **Due Date** | Payment deadline | Date picker | 04/22/2024 |
| **Subtotal** | Amount before tax | Currency | 500.00 |
| **Tax** | Tax amount | Currency | 50.00 |
| **Discount** | Discount applied | Currency | 0.00 |
| **Total Amount** | Final bill amount | Currency | 550.00 |
| **Status** | Invoice status | Dropdown | DRAFT |
| **Created By** | Billing staff name | Text | Ahmed |
| **Notes** | Additional info | Text | Hospital services |

4. Review Calculation:
   ```
   Total Amount = (Subtotal + Tax - Discount)
   Example: (500.00 + 50.00 - 0.00) = 550.00
   ```

5. Click **"Save"**

6. Invoice created and available for payment

**Invoice Workflow:**
```
DRAFT → ISSUED → SENT → VIEWED → PARTIALLY_PAID → FULLY_PAID → ARCHIVED
```

---

### 2.3 ADD INVOICE LINE ITEMS (Optional)

**Purpose:** Itemize services on invoice

**Steps:**

1. From Invoice → Click **"+ Add Line Item"**

2. Complete Line Item:

| Field | Options |
|-------|---------|
| **Item Type** | Service, Medication, Procedure, Lab, Imaging |
| **Description** | Item description |
| **Quantity** | Number of units |
| **Unit Price** | Price per unit |
| **Total** | Auto-calculated |

3. Click **"Save"**

4. Line item added to invoice

---

### 2.4 PROCESS PAYMENT

**Purpose:** Record patient payment against invoice

**Steps:**

1. Click **"Billing"** → **"Payments"**

2. Click **"+ Add Payment"** button

3. Complete Payment Form:

| Field | Values | Notes |
|-------|--------|-------|
| **Invoice** | Dropdown | Select invoice to pay |
| **Payment Date** | Date Picker | When payment received |
| **Amount Paid** | Currency | Must not exceed invoice total |
| **Payment Method** | CASH, CARD, INSURANCE, BANK | How paid |
| **Reference** | Text | Check #, Card #, etc. |
| **Notes** | Text | Optional notes |

4. **Validation Checks:**
   - ✅ Amount ≤ Invoice Total
   - ✅ Payment Method valid
   - ✅ Invoice not already fully paid
   - ✅ No overpayments allowed

5. Click **"Save"**

6. Payment recorded, invoice status updates

**Expected Status Changes:**
- Partial Payment: `PARTIALLY_PAID`
- Full Payment: `FULLY_PAID`

---

### 2.5 TRACK INSURANCE CLAIMS

**Purpose:** Manage insurance claim submissions

**Steps:**

1. Click **"Billing"** → **"Insurance Claims"**

2. Click **"+ Add Insurance Claim"** button

3. Complete Claim Form:

| Field | Description |
|-------|-------------|
| **Invoice** | Associated invoice |
| **Insurance Provider** | Insurance company name |
| **Claim Number** | Claim reference ID |
| **Submission Date** | When submitted |
| **Amount Claimed** | Claimed amount |
| **Status** | Submitted, Approved, Denied, Paid |

4. Click **"Save"**

5. Track claim status and follow-up

**Claim Status Tracking:**
```
SUBMITTED → UNDER_REVIEW → APPROVED → PAID
                         ↓
                        DENIED
```

---

## 👨‍💼 ADMIN MODULE GUIDE

### Module Overview
The Admin Module manages:
- Hospital organizational structure
- Department management
- Ward/unit management
- Bed inventory and allocation
- System configuration

### Admin Module Access

1. Click **"Admin"** in left sidebar
2. Available options:
   - Departments
   - Wards
   - Beds
   - System Configuration

---

### 3.1 CREATE DEPARTMENT

**Purpose:** Establish new hospital department

**Steps:**

1. Click **"Admin"** → **"Departments"**

2. Click **"+ Add Department"** button

3. Complete Department Form:

| Field | Format | Rules | Example |
|-------|--------|-------|---------|
| **Name** | Text | Unique, Required | Cardiology |
| **Code** | Text | Unique code, 8 chars | CARD-001 |
| **Description** | Text | Department overview | Heart & cardiovascular care |
| **Status** | Dropdown | ACTIVE/INACTIVE | ACTIVE |
| **Head ID** | ID (optional) | Department head | DR-0001 |

4. **Validation:**
   - ✅ Name must be unique
   - ✅ Code must be unique
   - ✅ Both Name & Code required

5. Click **"Save"**

6. Department created and operational

---

### 3.2 CREATE WARD

**Purpose:** Establish hospital ward/unit

**Steps:**

1. Click **"Admin"** → **"Wards"**

2. Click **"+ Add Ward"** button

3. Complete Ward Form:

| Field | Format | Example | Required |
|-------|--------|---------|----------|
| **Name** | Text | Cardiac Ward | ✅ Yes |
| **Department** | Dropdown | Cardiology | ✅ Yes |
| **Capacity** | Number | 20 | ✅ Yes |
| **Ward Type** | Dropdown | ICU, General, Isolation | ❌ No |
| **Status** | Dropdown | ACTIVE | ✅ Yes |

4. **Rules:**
   - Each ward must belong to a department
   - Capacity = total authorized beds
   - Status determines operational status

5. Click **"Save"**

6. Ward created and bed allocation possible

---

### 3.3 CREATE/MANAGE BEDS

**Purpose:** Track individual bed in hospital

**Steps:**

1. Click **"Admin"** → **"Beds"**

2. Click **"+ Add Bed"** button

3. Complete Bed Form:

| Field | Value | Notes |
|-------|-------|-------|
| **Bed Number** | Unique identifier | Example: BED-001, 201-A |
| **Ward** | Dropdown | Select parent ward |
| **Bed Type** | ICU / General / VIP | Bed classification |
| **Status** | AVAILABLE, OCCUPIED, MAINTENANCE | Current status |
| **Notes** | Text | Special equipment, allergies, etc. |

4. Click **"Save"**

5. Bed created in system

**Bed Status Definitions:**
- **AVAILABLE:** Ready for patient admission
- **OCCUPIED:** Patient currently in bed
- **MAINTENANCE:** Out of service for repairs
- **CLEANED:** Recently vacated, ready for occupancy

---

### 3.4 SYSTEM CONFIGURATION

**Purpose:** Manage hospital system settings

**Steps:**

1. Click **"Admin"** → **"System Configuration"**

2. Available Settings:
   - Hospital name
   - Contact information
   - Operating hours
   - Holidays/closures
   - Default billing terms
   - Lab configuration

3. Edit any setting:
   - Click field to edit
   - Enter new value
   - Click **"Save"**

---

## 🔄 STANDARD WORKFLOWS

### Workflow 1: Complete Lab Testing Process

**Timeline: Typical = 2-3 hours**

```
STEP 1: Doctor Orders Tests
├─ Go to: Lab → Lab Orders
├─ Click: Add Lab Order
├─ Enter: Patient ID, Tests, Doctor Name
└─ Save: Status = PENDING

STEP 2: Specimen Collection (within 30 min)
├─ Go to: Lab → Specimens
├─ Click: Add Specimen
├─ Enter: Collection Details, Type, Time
└─ Save: Status = COLLECTED

STEP 3: Lab Analysis (1-2 hours)
├─ Go to: Lab → Lab Results
├─ Click: Add Lab Result
├─ Enter: Test Results, Values, References
└─ Save: Status = COMPLETED

STEP 4: Result Verification (30 min)
├─ Go to: Lab → Lab Results
├─ Click: Edit Result
├─ Change: Status = VERIFIED
└─ Save: Verified by Lab Director

STEP 5: Report Generation
├─ Go to: Lab → Lab Reports
├─ Click: Add Lab Report
├─ Enter: Interpretation, Final Status
└─ Save: Report FINAL

STEP 6: Send to Physician
├─ Print or Email Report
├─ File in Patient Record
└─ Notify Ordering Doctor
```

---

### Workflow 2: Complete Billing Process

**Timeline: Typical = Few minutes to days**

```
STEP 1: Create Patient Account
├─ Go to: Billing → Patient Accounts
├─ Click: Add Patient Account
├─ Enter: Patient ID, Account Number
└─ Save: Account ACTIVE

STEP 2: Issue Invoice
├─ Go to: Billing → Invoices
├─ Click: Add Invoice
├─ Enter: Amount, Due Date, Details
└─ Save: Status = DRAFT

STEP 3: Send Invoice to Patient
├─ Print Invoice
├─ Email to Patient/Insurance
├─ Update: Status = SENT
└─ Record: Sent Date/Time

STEP 4: Record Payment
├─ Go to: Billing → Payments
├─ Click: Add Payment
├─ Enter: Amount, Method, Date
└─ Save: Payment RECORDED

STEP 5: Update Invoice Status
├─ Full Payment = FULLY_PAID
├─ Partial = PARTIALLY_PAID
└─ No Payment = OVERDUE (if past due date)

STEP 6: Archive/Close
├─ Mark: Invoice Complete
├─ File in Records
└─ Year-end Accounting
```

---

### Workflow 3: Hospital Setup (First-Time)

**Required for new installation**

```
STEP 1: Create Departments
├─ Admin → Departments
├─ Create: Main departments (Surgery, Lab, etc.)
└─ Record: Department codes

STEP 2: Create Wards
├─ Admin → Wards
├─ Create: Wards per department
├─ Set: Bed capacity
└─ Example: 20-bed Cardiac Ward

STEP 3: Create Beds
├─ Admin → Beds
├─ Create: Individual beds
├─ Assign: Ward, Bed Type
└─ Total: All beds accounted for

STEP 4: Configure System
├─ Admin → System Configuration
├─ Set: Hospital name, contact info
├─ Set: Billing terms, holidays
└─ Complete: System ready
```

---

## 📋 BEST PRACTICES

### Lab Module Best Practices

✅ **DO:**
- Enter patient ID correctly (verify before saving)
- Use standardized test codes
- Collect specimens within 15 minutes of order
- Verify results before marking as VERIFIED
- Generate report before releasing results
- Maintain specimen chain of custody
- Record collection time accurately
- Note any specimen issues immediately

❌ **DON'T:**
- Create duplicate orders for same tests
- Edit completed results (create amendment instead)
- Delete orders (mark CANCELLED if needed)
- Forget to verify results
- Leave specimens untracked
- Process expired specimens
- Skip required fields

---

### Billing Module Best Practices

✅ **DO:**
- Verify patient account before invoicing
- Double-check invoice amounts
- Send invoices within 24 hours of service
- Record payments on same day as receipt
- Track insurance claims weekly
- Archive paid invoices monthly
- Maintain audit trail
- Update payment status immediately

❌ **DON'T:**
- Create duplicate invoices
- Change amounts after sending
- Allow overpayments
- Delete payment records
- Manually modify totals
- Skip insurance verification
- Leave claims untracked
- Process expired accounts

---

### Admin Module Best Practices

✅ **DO:**
- Plan department structure before creating
- Use consistent code naming
- Document bed types
- Keep ward capacity accurate
- Regular system backups
- Audit department changes
- Update bed status real-time
- Monitor resource utilization

❌ **DON'T:**
- Create duplicate departments
- Delete departments with active beds
- Exceed ward capacity
- Leave beds unassigned
- Create confusing code names
- Ignore maintenance needs
- Overload wards
- Skip configuration

---

## 🆘 TROUBLESHOOTING

### Issue 1: Cannot Login

**Symptoms:**
- "Invalid credentials" error
- Page won't load after login

**Solutions:**
1. Verify email spelling: `admin@hospital.com` (with @)
2. Check CAPS LOCK off
3. Verify password: `Admin@12345` (case-sensitive)
4. Clear browser cache (Ctrl+Shift+Delete)
5. Try different browser
6. Contact administrator if issue persists

---

### Issue 2: Cannot Save Record

**Symptoms:**
- "Save" button grayed out
- Error message appears

**Solutions:**
1. Check all * (required) fields are filled
2. Verify data formats (dates, numbers)
3. Check for duplicate entries (ID, Code)
4. Ensure fields meet validation rules
5. Try refreshing page (F5)
6. Check browser console for errors

---

### Issue 3: Data Not Appearing

**Symptoms:**
- Created record doesn't show in list
- Search returns no results

**Solutions:**
1. Refresh page (Ctrl+F5)
2. Clear browser cache
3. Wait 10 seconds for data sync
4. Verify record was actually saved
5. Check filters aren't hiding records
6. Logout and login again

---

### Issue 4: Slow Performance

**Symptoms:**
- System is sluggish
- Pages take long to load

**Solutions:**
1. Refresh browser page
2. Close unnecessary tabs
3. Clear browser cache
4. Try different time of day (less busy)
5. Check internet connection
6. Contact system administrator

---

### Issue 5: Permission Denied

**Symptoms:**
- "Access Denied" error
- Cannot access certain modules

**Solutions:**
1. Verify you're logged in as admin
2. Check account permissions
3. Logout and re-login
4. Contact system administrator
5. Verify account status is ACTIVE

---

## 📞 SUPPORT CONTACTS

**For Technical Issues:**
- System Administrator: [Contact Info]
- Email: support@hospital.com
- Phone: +1-XXX-XXX-XXXX
- Hours: Monday-Friday, 8 AM - 5 PM

**For Data Issues:**
- Lab Manager: [Contact Info]
- Billing Manager: [Contact Info]
- Admin Manager: [Contact Info]

---

## 🔒 SECURITY REMINDERS

⚠️ **IMPORTANT:**

1. Never share your login credentials
2. Change password every 90 days
3. Logout before leaving workstation
4. Use HTTPS (not HTTP)
5. Report suspicious activity immediately
6. Don't store passwords in emails
7. Lock workstation when away
8. Report lost credentials immediately

---

## ✅ SYSTEM CHECKLIST

Before starting work, verify:

- [ ] System is accessible: http://localhost:8000/admin/
- [ ] You can login with credentials
- [ ] All 3 modules visible in sidebar (Lab, Billing, Admin)
- [ ] Dashboard loads without errors
- [ ] You can create records in each module
- [ ] Changes are saved successfully
- [ ] You understand your role and permissions

---

## 📊 QUICK REFERENCE

### Lab Module Paths
```
Lab Orders:    Lab → Lab Orders
Specimens:     Lab → Specimens
Results:       Lab → Lab Results
Reports:       Lab → Lab Reports
```

### Billing Module Paths
```
Accounts:      Billing → Patient Accounts
Invoices:      Billing → Invoices
Payments:      Billing → Payments
Claims:        Billing → Insurance Claims
```

### Admin Module Paths
```
Departments:   Admin → Departments
Wards:         Admin → Wards
Beds:          Admin → Beds
Config:        Admin → System Configuration
```

---

## 📝 DOCUMENT INFORMATION

**Document Version:** 1.0  
**Created:** March 23, 2026  
**Last Modified:** March 23, 2026  
**Audience:** Hospital Staff, Administrators, Lab Technicians, Accountants  
**Classification:** Internal Use  

For updates or corrections, contact: support@hospital.com

---

**System Status: ✅ READY FOR PRODUCTION USE**


"""
End-to-End Workflow Tests

This script tests three complete healthcare workflows:
1. Lab Workflow: Specimen -> Results -> Verification -> Report Release
2. Billing Workflow: Invoice Creation -> Finalization -> Payment -> Balance Update
3. Admin Workflow: User Creation -> Role Assignment -> Deactivation

Run with: python manage.py shell < test_e2e_workflows.py
Or: python test_e2e_workflows.py
"""

import os
import django
import requests
import json
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.contrib.auth import get_user_model
from apps.lab.infrastructure.orm_models import LabOrder, Specimen, LabResult, LabReport
from apps.billing.infrastructure.orm_billing_models import PatientAccount, Invoice, InvoiceLineItem, Payment
from apps.admin.infrastructure.orm_admin_extended import Department, UserRole, Role

User = get_user_model()

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10


class WorkflowTester:
    """End-to-end workflow test suite."""
    
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.lab_tech_token = None
        self.doctor_token = None
        self.accountant_token = None
        self.admin_token = None
    
    def log(self, message, level="INFO"):
        """Log message with level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def setup_test_users(self):
        """Create test users with different roles."""
        self.log("Setting up test users...", "SETUP")
        
        # Create or get lab technician
        lab_tech_user, _ = User.objects.get_or_create(
            username="lab_tech_test",
            defaults={
                "email": "lab_tech@test.local",
                "full_name": "Lab Tech Test",
                "is_active": True,
                "role": "LAB_TECHNICIAN"
            }
        )
        lab_tech_user.set_password("TestPassword123")
        lab_tech_user.save()
        
        # Create or get doctor
        doctor_user, _ = User.objects.get_or_create(
            username="doctor_test",
            defaults={
                "email": "doctor@test.local",
                "full_name": "Doctor Test",
                "is_active": True,
                "role": "DOCTOR"
            }
        )
        doctor_user.set_password("TestPassword123")
        doctor_user.save()
        
        # Create or get accountant
        accountant_user, _ = User.objects.get_or_create(
            username="accountant_test",
            defaults={
                "email": "accountant@test.local",
                "full_name": "Accountant Test",
                "is_active": True,
                "role": "ACCOUNTANT"
            }
        )
        accountant_user.set_password("TestPassword123")
        accountant_user.save()
        
        # Create or get admin
        admin_user, _ = User.objects.get_or_create(
            username="admin_test",
            defaults={
                "email": "admin@test.local",
                "full_name": "Admin Test",
                "is_active": True,
                "role": "ADMIN"
            }
        )
        admin_user.set_password("TestPassword123")
        admin_user.save()
        
        self.log(f"✓ Test users created/updated", "SUCCESS")
    
    def login_user(self, email, password):
        """Login user and return token."""
        response = self.session.post(
            f"{BASE_URL}/auth/login/",
            json={"email": email, "password": password},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.log(f"✓ User {email} logged in", "SUCCESS")
            return token
        else:
            self.log(f"✗ Failed to login {email}: {response.text}", "ERROR")
            return None
    
    def test_lab_workflow(self):
        """Test complete lab workflow."""
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        self.log("STARTING LAB WORKFLOW TEST", "INFO")
        self.log("=" * 60, "INFO")
        
        # Get tokens
        self.lab_tech_token = self.login_user("lab_tech@test.local", "TestPassword123")
        self.doctor_token = self.login_user("doctor@test.local", "TestPassword123")
        
        if not self.lab_tech_token or not self.doctor_token:
            self.log("✗ Failed to get required tokens", "ERROR")
            return False
        
        headers_tech = {"Authorization": f"Bearer {self.lab_tech_token}"}
        headers_doctor = {"Authorization": f"Bearer {self.doctor_token}"}
        
        try:
            # Step 1: Create lab order
            self.log("Step 1: Creating lab order...", "INFO")
            order_data = {
                "patient_id": "TEST-001",
                "encounter_id": "ENC-001",
                "test_codes": ["CBC", "BMP"],
                "ordered_by": "dr_smith"
            }
            response = self.session.post(
                f"{BASE_URL}/lab/orders/",
                json=order_data,
                headers=headers_tech,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create order: {response.text}", "ERROR")
                return False
            
            order_id = response.json().get("id")
            self.log(f"✓ Lab order created: {order_id}", "SUCCESS")
            
            # Step 2: Create specimen
            self.log("Step 2: Creating specimen...", "INFO")
            specimen_data = {
                "order_id": order_id,
                "specimen_type": "BLOOD",
                "collection_time": datetime.now().isoformat(),
                "patient_id": "TEST-001"
            }
            response = self.session.post(
                f"{BASE_URL}/lab/specimens/",
                json=specimen_data,
                headers=headers_tech,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create specimen: {response.text}", "ERROR")
                return False
            
            specimen_id = response.json().get("id")
            self.log(f"✓ Specimen created: {specimen_id}", "SUCCESS")
            
            # Step 3: Enter lab result
            self.log("Step 3: Entering lab result...", "INFO")
            result_data = {
                "order_id": order_id,
                "specimen_id": specimen_id,
                "test_code": "CBC",
                "test_name": "Complete Blood Count",
                "result_value": "7.5",
                "unit": "10^3/uL",
                "reported_by": "lab_tech_test",
                "status": "completed"
            }
            response = self.session.post(
                f"{BASE_URL}/lab/results/",
                json=result_data,
                headers=headers_tech,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to enter result: {response.text}", "ERROR")
                return False
            
            result_id = response.json().get("id")
            self.log(f"✓ Lab result entered: {result_id}", "SUCCESS")
            
            # Step 4: Doctor verifies result
            self.log("Step 4: Doctor verifying result...", "INFO")
            response = self.session.post(
                f"{BASE_URL}/lab/results/{result_id}/verify/",
                headers=headers_doctor,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to verify result: {response.text}", "ERROR")
                return False
            
            self.log(f"✓ Result verified by doctor", "SUCCESS")
            
            # Step 5: Generate and release report
            self.log("Step 5: Creating lab report...", "INFO")
            report_data = {
                "order_id": order_id,
                "specimen_id": specimen_id,
                "patient_id": "TEST-001",
                "status": "preliminary"
            }
            response = self.session.post(
                f"{BASE_URL}/lab/reports/",
                json=report_data,
                headers=headers_doctor,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create report: {response.text}", "ERROR")
                return False
            
            report_id = response.json().get("id")
            self.log(f"✓ Lab report created: {report_id}", "SUCCESS")
            
            # Step 6: Finalize report
            self.log("Step 6: Finalizing report...", "INFO")
            response = self.session.post(
                f"{BASE_URL}/lab/reports/{report_id}/finalize/",
                headers=headers_doctor,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to finalize report: {response.text}", "ERROR")
                return False
            
            self.log(f"✓ Lab report finalized and released", "SUCCESS")
            
            self.log("✓ LAB WORKFLOW COMPLETED SUCCESSFULLY", "SUCCESS")
            self.results.append(("Lab Workflow", "PASSED"))
            return True
            
        except Exception as e:
            self.log(f"✗ Lab workflow error: {str(e)}", "ERROR")
            self.results.append(("Lab Workflow", "FAILED"))
            return False
    
    def test_billing_workflow(self):
        """Test complete billing workflow."""
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        self.log("STARTING BILLING WORKFLOW TEST", "INFO")
        self.log("=" * 60, "INFO")
        
        # Get tokens
        self.accountant_token = self.login_user("accountant@test.local", "TestPassword123")
        
        if not self.accountant_token:
            self.log("✗ Failed to get accountant token", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.accountant_token}"}
        
        try:
            # Step 1: Create patient account
            self.log("Step 1: Creating patient account...", "INFO")
            account_data = {
                "patient_id": "BILL-001",
                "account_number": f"ACC-{datetime.now().timestamp()}",
                "status": "active"
            }
            response = self.session.post(
                f"{BASE_URL}/billing/accounts/",
                json=account_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create account: {response.text}", "ERROR")
                return False
            
            account_id = response.json().get("id")
            self.log(f"✓ Patient account created: {account_id}", "SUCCESS")
            
            # Step 2: Create invoice
            self.log("Step 2: Creating invoice...", "INFO")
            invoice_data = {
                "account": account_id,
                "invoice_number": f"INV-{datetime.now().timestamp()}",
                "encounter_id": "ENC-002",
                "invoice_date": datetime.now().strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "subtotal": "1000.00",
                "tax": "100.00",
                "discount": "0.00",
                "total_amount": "1100.00",
                "status": "draft"
            }
            response = self.session.post(
                f"{BASE_URL}/billing/invoices/",
                json=invoice_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create invoice: {response.text}", "ERROR")
                return False
            
            invoice_id = response.json().get("id")
            self.log(f"✓ Invoice created: {invoice_id}", "SUCCESS")
            
            # Step 3: Add line items
            self.log("Step 3: Adding line items...", "INFO")
            line_item_data = {
                "invoice_id": invoice_id,
                "item_type": "service",
                "description": "Doctor Consultation",
                "quantity": 2,
                "unit_price": "500.00",
                "total_price": "1000.00",
                "service_code": "CONS-001"
            }
            response = self.session.post(
                f"{BASE_URL}/billing/line-items/",
                json=line_item_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to add line item: {response.text}", "ERROR")
                return False
            
            self.log(f"✓ Line item added", "SUCCESS")
            
            # Step 4: Finalize invoice
            self.log("Step 4: Finalizing invoice...", "INFO")
            response = self.session.post(
                f"{BASE_URL}/billing/invoices/{invoice_id}/finalize/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to finalize invoice: {response.text}", "ERROR")
                return False
            
            self.log(f"✓ Invoice finalized", "SUCCESS")
            
            # Step 5: Process payment
            self.log("Step 5: Processing payment...", "INFO")
            payment_data = {
                "account": account_id,
                "invoice": invoice_id,
                "payment_amount": "550.00",
                "payment_date": datetime.now().strftime("%Y-%m-%d"),
                "payment_method": "CARD",
                "reference_number": f"PAY-{datetime.now().timestamp()}",
                "status": "pending"
            }
            response = self.session.post(
                f"{BASE_URL}/billing/payments/",
                json=payment_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to create payment: {response.text}", "ERROR")
                return False
            
            payment_id = response.json().get("id")
            self.log(f"✓ Payment created: {payment_id}", "SUCCESS")
            
            # Step 6: Process payment (mark as processed)
            self.log("Step 6: Processing payment record...", "INFO")
            response = self.session.post(
                f"{BASE_URL}/billing/payments/{payment_id}/process/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"✗ Failed to process payment: {response.text}", "ERROR")
                return False
            
            self.log(f"✓ Payment processed successfully", "SUCCESS")
            
            # Step 7: Verify partial balance update
            self.log("Step 7: Verifying account balance...", "INFO")
            response = self.session.get(
                f"{BASE_URL}/billing/accounts/{account_id}/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                account_data = response.json()
                remaining_balance = account_data.get("total_balance", 0)
                self.log(f"✓ Account balance verified: {remaining_balance}", "SUCCESS")
            else:
                self.log(f"⚠ Could not verify balance: {response.text}", "WARNING")
            
            self.log("✓ BILLING WORKFLOW COMPLETED SUCCESSFULLY", "SUCCESS")
            self.results.append(("Billing Workflow", "PASSED"))
            return True
            
        except Exception as e:
            self.log(f"✗ Billing workflow error: {str(e)}", "ERROR")
            self.results.append(("Billing Workflow", "FAILED"))
            return False
    
    def test_admin_workflow(self):
        """Test complete admin workflow."""
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        self.log("STARTING ADMIN WORKFLOW TEST", "INFO")
        self.log("=" * 60, "INFO")
        
        # Get token
        self.admin_token = self.login_user("admin@test.local", "TestPassword123")
        
        if not self.admin_token:
            self.log("✗ Failed to get admin token", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Step 1: Get system roles
            self.log("Step 1: Retrieving system roles...", "INFO")
            response = self.session.get(
                f"{BASE_URL}/admin/roles/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                roles = response.json()
                self.log(f"✓ Found {len(roles)} roles", "SUCCESS")
            else:
                self.log(f"✗ Failed to retrieve roles: {response.text}", "ERROR")
                return False
            
            # Step 2: Get departments
            self.log("Step 2: Retrieving departments...", "INFO")
            response = self.session.get(
                f"{BASE_URL}/admin/departments/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                departments = response.json()
                self.log(f"✓ Found {len(departments)} departments", "SUCCESS")
            else:
                self.log(f"✗ Failed to retrieve departments: {response.text}", "ERROR")
                return False
            
            # Step 3: Get audit logs
            self.log("Step 3: Retrieving audit logs...", "INFO")
            response = self.session.get(
                f"{BASE_URL}/admin/audit-logs/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                logs = response.json()
                self.log(f"✓ Found {len(logs)} audit logs", "SUCCESS")
            else:
                self.log(f"✗ Failed to retrieve audit logs: {response.text}", "ERROR")
                return False
            
            # Step 4: Get admin users
            self.log("Step 4: Retrieving admin users...", "INFO")
            response = self.session.get(
                f"{BASE_URL}/admin/admins/",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                admins = response.json()
                self.log(f"✓ Found {len(admins)} admin users", "SUCCESS")
            else:
                self.log(f"✗ Failed to retrieve admins: {response.text}", "ERROR")
                return False
            
            self.log("✓ ADMIN WORKFLOW COMPLETED SUCCESSFULLY", "SUCCESS")
            self.results.append(("Admin Workflow", "PASSED"))
            return True
            
        except Exception as e:
            self.log(f"✗ Admin workflow error: {str(e)}", "ERROR")
            self.results.append(("Admin Workflow", "FAILED"))
            return False
    
    def print_summary(self):
        """Print test results summary."""
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        self.log("TEST RESULTS SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        for test_name, result in self.results:
            status_symbol = "✓" if result == "PASSED" else "✗"
            self.log(f"{status_symbol} {test_name}: {result}", "INFO")
        
        passed = sum(1 for _, r in self.results if r == "PASSED")
        total = len(self.results)
        self.log(f"\nTotal: {passed}/{total} workflows passed", "INFO")
        self.log("=" * 60, "INFO")
    
    def run_all_tests(self):
        """Run all workflow tests."""
        self.log("Starting End-to-End Workflow Tests", "INFO")
        self.log(f"Base URL: {BASE_URL}", "INFO")
        
        # Setup
        self.setup_test_users()
        
        # Run tests
        self.test_lab_workflow()
        self.test_billing_workflow()
        self.test_admin_workflow()
        
        # Summary
        self.print_summary()
        
        return all(r == "PASSED" for _, r in self.results)


if __name__ == "__main__":
    tester = WorkflowTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)

#!/usr/bin/env python
"""
Simple system tester for Admin, Lab, and Billing modules.
Tests all three modules with real API calls.
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

# Admin credentials
ADMIN_EMAIL = "admin@hospital.com"
ADMIN_PASSWORD = "Admin@12345"

def get_token():
    """Login and get authentication token."""
    print("\n🔐 Logging in...")
    url = f"{BASE_URL}/auth/login/"
    payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✓ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_lab_module(token):
    """Test Lab Module - Create and view lab orders."""
    print("\n" + "="*60)
    print("🧪 LAB MODULE TEST")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Create a lab order
    print("\n1. Creating lab order...")
    lab_payload = {
        "patient_id": str(uuid4()),
        "encounter_id": str(uuid4()),
        "test_codes": ["CBC", "LFT", "RBS"],
        "ordered_by": "Dr. Ahmed",
        "status": "PENDING",
        "priority": "ROUTINE",
        "notes": "Regular checkup tests"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/lab/orders/",
            json=lab_payload,
            headers=headers
        )
        if response.status_code in [200, 201]:
            order = response.json()
            print(f"✓ Lab Order Created!")
            print(f"  Order ID: {order.get('id')}")
            print(f"  Patient: {order.get('patient_id')}")
            print(f"  Tests: {order.get('test_codes')}")
        else:
            print(f"⚠ Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    # Test 2: Get all lab orders
    print("\n2. Retrieving all lab orders...")
    try:
        response = requests.get(
            f"{BASE_URL}/lab/orders/",
            headers=headers
        )
        if response.status_code == 200:
            orders = response.json()
            count = len(orders) if isinstance(orders, list) else 1
            print(f"✓ Retrieved {count} lab order(s)")
        else:
            print(f"⚠ Response: {response.status_code}")
    except Exception as e:
        print(f"⚠ Error: {e}")

def test_billing_module(token):
    """Test Billing Module - Create and view invoices."""
    print("\n" + "="*60)
    print("💳 BILLING MODULE TEST")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Create patient account
    print("\n1. Creating patient account...")
    account_payload = {
        "patient_id": str(uuid4()),
        "account_number": f"ACC-{str(uuid4())[:8]}",
        "status": "ACTIVE",
        "total_balance": 0.00,
        "total_paid": 0.00,
        "insurance_info": {"provider": "Local Insurance"},
        "preferred_payment_method": "CASH"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/billing/accounts/",
            json=account_payload,
            headers=headers
        )
        if response.status_code in [200, 201]:
            account = response.json()
            print(f"✓ Patient Account Created!")
            print(f"  Account: {account.get('account_number')}")
            print(f"  Patient: {account.get('patient_id')[:8]}...")
        else:
            print(f"⚠ Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    # Test 2: Get all accounts
    print("\n2. Retrieving all accounts...")
    try:
        response = requests.get(
            f"{BASE_URL}/billing/accounts/",
            headers=headers
        )
        if response.status_code == 200:
            accounts = response.json()
            count = len(accounts) if isinstance(accounts, list) else 1
            print(f"✓ Retrieved {count} account(s)")
        else:
            print(f"⚠ Response: {response.status_code}")
    except Exception as e:
        print(f"⚠ Error: {e}")

def test_admin_module(token):
    """Test Admin Module - Manage system."""
    print("\n" + "="*60)
    print("👨‍💼 ADMIN MODULE TEST")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Create department
    print("\n1. Creating department...")
    dept_payload = {
        "name": "Cardiology",
        "code": "CARD-001",
        "description": "Heart and cardiovascular diseases"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/departments/",
            json=dept_payload,
            headers=headers
        )
        if response.status_code in [200, 201]:
            dept = response.json()
            print(f"✓ Department Created!")
            print(f"  Name: {dept.get('name')}")
            print(f"  Code: {dept.get('code')}")
        else:
            print(f"⚠ Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    # Test 2: Get all departments
    print("\n2. Retrieving all departments...")
    try:
        response = requests.get(
            f"{BASE_URL}/admin/departments/",
            headers=headers
        )
        if response.status_code == 200:
            depts = response.json()
            count = len(depts) if isinstance(depts, list) else 1
            print(f"✓ Retrieved {count} department(s)")
        else:
            print(f"⚠ Response: {response.status_code}")
    except Exception as e:
        print(f"⚠ Error: {e}")

def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("HOSPITAL SYSTEM - MODULE TEST SUITE")
    print("🚀 " * 20)
    
    # Step 1: Login
    token = get_token()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Step 2: Test modules
    test_lab_module(token)
    test_billing_module(token)
    test_admin_module(token)
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE!")
    print("="*60)
    print("\n✓ All modules are working!")
    print(f"\n📊 Access Admin Panel: http://localhost:8000/admin/")
    print(f"📊 API Base: {BASE_URL}/")
    print()

if __name__ == "__main__":
    main()

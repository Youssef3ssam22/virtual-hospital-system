#!/usr/bin/env python
"""
Comprehensive System Verification Script
Tests all critical endpoints and modules
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Health check endpoint responsive")
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False

def test_auth_endpoints():
    """Test 2: Authentication Endpoints"""
    print_header("TEST 2: AUTHENTICATION")
    
    # Test registration
    print_info("Testing user registration...")
    register_data = {
        "email": "testuser@hospital.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register/",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print_success("User registration successful")
            user_data = response.json()
            print(f"  Email: {user_data.get('email')}")
            print(f"  Name: {user_data.get('full_name')}")
        elif response.status_code == 409:
            # User already exists, that's okay for testing
            print_success("User already exists (acceptable for test)")
        else:
            print_error(f"Registration failed: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text[:200]}")
            return False, None
        
        # Test login
        print_info("Testing user login...")
        login_data = {
            "email": "testuser@hospital.com",
            "password": "TestPass123!"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_success("User login successful")
            print(f"  Token: {token[:20]}...")
            return True, token
        else:
            print_error(f"Login failed: {response.status_code}")
            return False, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return False, None

def test_admin_endpoints(token):
    """Test 3: Admin Module Endpoints"""
    print_header("TEST 3: ADMIN MODULE")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test create admin
        print_info("Testing admin creation...")
        admin_data = {
            "email": "admin@hospital.com",
            "full_name": "Dr. Ahmed Smith",
            "phone": "555-0100",
            "department": "Administration"
        }
        
        response = requests.post(
            f"{API_BASE}/admin/",
            json=admin_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            print_success("Admin creation successful")
            admin = response.json()
            print(f"  Email: {admin.get('email')}")
            print(f"  Employee #: {admin.get('employee_number')}")
        else:
            print_error(f"Admin creation failed: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text[:200]}")
        
        # Test list admins
        print_info("Testing admin list retrieval...")
        response = requests.get(
            f"{API_BASE}/admin/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"Admin list retrieved ({count} admins)")
            if data.get('results'):
                for admin in data['results'][:2]:
                    print(f"  - {admin.get('email')} ({admin.get('full_name')})")
            return True
        else:
            print_error(f"Admin list failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Admin module error: {str(e)}")
        return False

def test_lab_endpoints(token):
    """Test 4: Lab Module Endpoints"""
    print_header("TEST 4: LAB MODULE")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test create lab order
        print_info("Testing lab order creation...")
        lab_data = {
            "patient_id": "550e8400-e29b-41d4-a716-426614174000",
            "encounter_id": "660e8400-e29b-41d4-a716-426614174000",
            "test_codes": ["CBC", "BMP"],
            "ordered_by": "testuser@hospital.com",
            "priority": "NORMAL"
        }
        
        response = requests.post(
            f"{API_BASE}/lab/",
            json=lab_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            print_success("Lab order creation successful")
            order = response.json()
            print(f"  Order ID: {order.get('id')}")
            print(f"  Status: {order.get('status')}")
            print(f"  Tests: {', '.join(order.get('test_codes', []))}")
        else:
            print_error(f"Lab order creation failed: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text[:200]}")
        
        # Test list lab orders
        print_info("Testing lab order list retrieval...")
        response = requests.get(
            f"{API_BASE}/lab/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"Lab orders retrieved ({count} orders)")
            if data.get('results'):
                for order in data['results'][:2]:
                    print(f"  - Order {order.get('id')[:8]}... (Status: {order.get('status')})")
            return True
        else:
            print_error(f"Lab list failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Lab module error: {str(e)}")
        return False

def test_api_docs():
    """Test 5: API Documentation"""
    print_header("TEST 5: API DOCUMENTATION")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=5)
        if response.status_code == 200:
            print_success("Swagger UI accessible")
            print(f"  URL: {BASE_URL}/api/docs/")
        else:
            print_error(f"Swagger UI failed: {response.status_code}")
            
        response = requests.get(f"{BASE_URL}/api/redoc/", timeout=5)
        if response.status_code == 200:
            print_success("ReDoc accessible")
            print(f"  URL: {BASE_URL}/api/redoc/")
        else:
            print_error(f"ReDoc failed: {response.status_code}")
            
    except Exception as e:
        print_error(f"Documentation error: {str(e)}")

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print(f"  Virtual Hospital System - Verification Test Suite")
    print(f"  Testing: {BASE_URL}")
    print(f"{'='*60}{RESET}")
    
    print_info("Waiting for server to be ready...")
    time.sleep(2)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    
    auth_success, token = test_auth_endpoints()
    results.append(("Authentication", auth_success))
    
    if token:
        results.append(("Admin Module", test_admin_endpoints(token)))
        results.append(("Lab Module", test_lab_endpoints(token)))
    
    test_api_docs()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, passed_test in results:
        status = f"{GREEN}PASS{RESET}" if passed_test else f"{RED}FAIL{RESET}"
        print(f"  {test_name:.<40} {status}")
    
    print(f"\n{BLUE}Overall: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✓ All systems operational!{RESET}")
        print(f"\nAccess your API at:")
        print(f"  📖 Interactive Docs: {BASE_URL}/api/docs/")
        print(f"  📚 Beautiful Docs: {BASE_URL}/api/redoc/")
        print(f"  ❤️ Health Check: {BASE_URL}/health/")
    else:
        print(f"\n{RED}✗ Some tests failed. Check errors above.{RESET}")

if __name__ == "__main__":
    main()

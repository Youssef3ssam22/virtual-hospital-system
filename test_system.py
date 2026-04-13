#!/usr/bin/env python
"""Test script to verify all systems are working."""

import requests
import sys

url = 'http://localhost:8000'
print('=== Testing Virtual Hospital System ===')
print()

all_pass = True

# Test 1: Health Check
print('1. Health Check:')
try:
    r = requests.get(url + '/health/')
    print('   Overall Status: ' + str(r.status_code))
    if r.status_code == 200:
        data = r.json()
        status = data['status']
        checks = data['checks']
        print('   System Status: ' + status)
        print('   Database: ' + checks['database'])
        print('   Redis: ' + checks['redis'])
        print('   Neo4j: ' + checks['neo4j'])
    else:
        all_pass = False
except Exception as e:
    print('   Error: ' + str(e))
    all_pass = False

# Test 2: API Documentation
print()
print('2. API Documentation:')
try:
    r = requests.get(url + '/api/docs/')
    sw_status = r.status_code
    print('   Swagger UI: ' + str(sw_status))
    r = requests.get(url + '/api/redoc/')
    red_status = r.status_code
    print('   ReDoc: ' + str(red_status))
    if sw_status != 200 or red_status != 200:
        all_pass = False
except Exception as e:
    print('   Error: ' + str(e))
    all_pass = False

# Test 3: Lab API
print()
print('3. Lab API Endpoints:')
try:
    r = requests.get(url + '/api/v1/lab/')
    print('   GET /api/v1/lab/ Status: ' + str(r.status_code) + ' (should be 403 - auth required)')
    if r.status_code != 403:
        all_pass = False
except Exception as e:
    print('   Error: ' + str(e))
    all_pass = False

# Test 4: Admin API  
print()
print('4. Admin API Endpoints:')
try:
    r = requests.get(url + '/api/v1/admin/')
    print('   GET /api/v1/admin/ Status: ' + str(r.status_code) + ' (should be 403 - auth required)')
    if r.status_code != 403:
        all_pass = False
except Exception as e:
    print('   Error: ' + str(e))
    all_pass = False

# Test 5: Patients API
print()
print('5. Patients API Endpoints:')
try:
    r = requests.get(url + '/api/v1/patients/')
    print('   GET /api/v1/patients/ Status: ' + str(r.status_code) + ' (should be 403 - auth required)')
    if r.status_code != 403:
        all_pass = False
except Exception as e:
    print('   Error: ' + str(e))
    all_pass = False

print()
if all_pass:
    print('=== SUCCESS: All Core Systems Operational ===')
    sys.exit(0)
else:
    print('=== WARNING: Some systems may have issues ===')
    sys.exit(1)

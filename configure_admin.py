#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.auth.infrastructure.orm_models import User

try:
    u = User.objects.get(email='admin@hospital.com')
    u.set_password('Admin@12345')
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.save()
    print("Admin user configured successfully!")
    print(f"Email: {u.email}")
    print(f"Full Name: {u.full_name}")
    print(f"Is Staff: {u.is_staff}")
    print(f"Is Superuser: {u.is_superuser}")
    print(f"Is Active: {u.is_active}")
    print("\nYou can now login to admin at:")
    print("http://localhost:8000/admin/")
    print("Email: admin@hospital.com")
    print("Password: Admin@12345")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.auth.infrastructure.orm_models import User

try:
    u = User.objects.get(email='admin@hospital.com')
    u.set_password('Admin@12345')
    u.save()
    print("Password set successfully!")
    print("Email: " + str(u.email))
    print("Full Name: " + str(u.full_name))
    print("Is Active: " + str(u.is_active))
except Exception as e:
    print("Error: " + str(e))

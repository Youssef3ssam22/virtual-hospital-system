#!/usr/bin/env python
"""Check admin user in database."""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.auth.infrastructure.orm_models import User

print("Checking users in database...\n")

users = User.objects.all()
print(f"Total users: {users.count()}\n")

for user in users:
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Name: {user.full_name}")
    print(f"Active: {user.is_active}")
    print(f"Superuser: {user.is_superuser}")
    print(f"---")

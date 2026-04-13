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
    print("✅ تم تعيين كلمة المرور بنجاح!")
    print(f"Email: {u.email}")
    print(f"Full Name: {u.full_name}")
    print(f"Is Active: {u.is_active}")
    print("\nيمكنك الآن تسجيل الدخول في:")
    print("http://localhost:8000/admin/")
    print("Email: admin@hospital.com")
    print("Password: Admin@12345")
except User.DoesNotExist:
    print("❌ لم يتم العثور على المستخدم!")
except Exception as e:
    print(f"❌ خطأ: {e}")

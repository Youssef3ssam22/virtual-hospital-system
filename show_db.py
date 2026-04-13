#!/usr/bin/env python
"""Show database tables and sample data."""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.db import connection
from django.apps import apps

print("=" * 80)
print("DATABASE TABLES & MODULES")
print("=" * 80)

# Show all models in the database
models = apps.get_models()
print(f"\n📊 Total Models: {len(models)}\n")

for model in models:
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    table_name = model._meta.db_table
    count = model.objects.count()
    print(f"✓ {app_label:15} → {model_name:20} | Table: {table_name:30} | Records: {count}")

print("\n" + "=" * 80)
print("ADMIN MODULE DATA")
print("=" * 80)

try:
    from apps.admin.infrastructure.orm_models import AdminUser
    admins = AdminUser.objects.all()
    if admins.exists():
        print(f"\nAdmins ({admins.count()}):")
        for admin in admins[:5]:
            print(f"  • {admin.full_name} ({admin.email}) - Role: {admin.role}")
    else:
        print("\n❌ No admins found")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("LAB MODULE DATA")
print("=" * 80)

try:
    from apps.lab.infrastructure.orm_models import LabOrder, Specimen, LabResult
    orders = LabOrder.objects.all()
    if orders.exists():
        print(f"\nLab Orders ({orders.count()}):")
        for order in orders[:5]:
            print(f"  • Order ID: {order.id} | Patient: {order.patient_id} | Status: {order.status}")
    else:
        print("\n✓ No lab orders yet (Ready for testing)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("BILLING MODULE DATA")
print("=" * 80)

try:
    from apps.billing.infrastructure.orm_billing_models import PatientAccount, Invoice, Payment
    accounts = PatientAccount.objects.all()
    if accounts.exists():
        print(f"\nPatient Accounts ({accounts.count()}):")
        for account in accounts[:5]:
            print(f"  • Account: {account.account_number} | Patient: {account.patient_id} | Balance: {account.total_balance}")
    else:
        print("\n✓ No billing accounts yet (Ready for testing)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)

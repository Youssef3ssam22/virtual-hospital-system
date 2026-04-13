"""Management command to create an admin user for local/dev use."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.auth.infrastructure.orm_models import User
from apps.admin.infrastructure.orm_models import AdminUser
from apps.admin.infrastructure.orm_admin_extended import Role, UserRole
from shared.constants.roles import Role as RoleConstants


class Command(BaseCommand):
    help = "Create or update a default admin user."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@hospital.com")
        parser.add_argument("--password", default="Admin@12345")
        parser.add_argument("--name", default="System Admin")
        parser.add_argument("--employee-number", default=None)
        parser.add_argument("--phone", default=None)

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        full_name = options["name"].strip() if options["name"] else "System Admin"
        employee_number = options["employee_number"]
        phone = options["phone"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        # Ensure admin flags and password are set even on reruns.
        user.full_name = full_name
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.set_password(password)
        user.save()

        if not employee_number:
            employee_number = _next_employee_number()

        AdminUser.objects.get_or_create(
            email=email,
            defaults={
                "employee_number": employee_number,
                "full_name": full_name,
                "role": "ADMIN",
                "phone": phone,
                "is_active": True,
            },
        )

        admin_role, _ = Role.objects.get_or_create(
            code=RoleConstants.ADMIN,
            defaults={
                "name": "Admin",
                "description": "System administrator",
                "is_system_role": True,
            },
        )

        UserRole.objects.get_or_create(user_id=str(user.id), role=admin_role, defaults={"assigned_by": "system"})
        UserRole.objects.filter(user_id=str(user.id), role=admin_role).update(
            is_primary=True,
            status="active",
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin user created: {email}"))
        else:
            self.stdout.write(self.style.WARNING(f"Admin user already exists: {email}"))


def _next_employee_number() -> str:
    prefix = "ADM"
    counter = AdminUser.objects.count() + 1
    while True:
        candidate = f"{prefix}{counter:04d}"
        if not AdminUser.objects.filter(employee_number=candidate).exists():
            return candidate
        counter += 1

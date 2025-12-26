from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from employees.models import Department, Role


class Command(BaseCommand):
    help = "Seed initial roles, departments, and demo users for EMS"

    def handle(self, *args, **options):
        # Roles
        roles = [
            ("Admin", "Administrator role with elevated privileges"),
            ("Manager", "Manager role with edit permissions"),
            ("Employee", "Standard employee role"),
        ]
        created_roles = []
        for name, desc in roles:
            obj, created = Role.objects.get_or_create(name=name, defaults={"description": desc})
            if created:
                created_roles.append(name)

        # Departments
        departments = [
            ("Engineering", "Engineering department"),
            ("HR", "Human Resources"),
            ("Finance", "Finance department"),
        ]
        created_depts = []
        for name, desc in departments:
            obj, created = Department.objects.get_or_create(name=name, defaults={"description": desc})
            if created:
                created_depts.append(name)

        # Users
        User = get_user_model()

        # Admin user
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
            },
        )
        if created or not admin.has_usable_password():
            admin.set_password("Admin@123")
            admin.is_staff = True
            admin.save()
        admin_role = Role.objects.get(name="Admin")
        admin.roles.add(admin_role)

        # Manager user
        mgr, created = User.objects.get_or_create(
            username="manager",
            defaults={
                "email": "manager@example.com",
            },
        )
        if created or not mgr.has_usable_password():
            mgr.set_password("Manager@123")
            mgr.save()
        mgr_role = Role.objects.get(name="Manager")
        mgr.roles.add(mgr_role)
        mgr.department = Department.objects.get(name="Engineering")
        mgr.save()

        # Employee user
        emp, created = User.objects.get_or_create(
            username="employee",
            defaults={
                "email": "employee@example.com",
            },
        )
        if created or not emp.has_usable_password():
            emp.set_password("Employee@123")
            emp.save()
        emp_role = Role.objects.get(name="Employee")
        emp.roles.add(emp_role)
        emp.department = Department.objects.get(name="Engineering")
        emp.save()

        # Summary output
        if created_roles:
            self.stdout.write(self.style.SUCCESS(f"Created roles: {', '.join(created_roles)}"))
        if created_depts:
            self.stdout.write(self.style.SUCCESS(f"Created departments: {', '.join(created_depts)}"))
        self.stdout.write(self.style.SUCCESS("Seed complete"))
        self.stdout.write("Credentials:")
        self.stdout.write(" - admin / Admin@123 (is_staff)")
        self.stdout.write(" - manager / Manager@123")
        self.stdout.write(" - employee / Employee@123")

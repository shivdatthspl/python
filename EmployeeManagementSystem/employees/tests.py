from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Department, Role


User = get_user_model()


class EmployeeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dept = Department.objects.create(name="Engineering")
        self.admin_role = Role.objects.create(name="Admin")
        self.manager_role = Role.objects.create(name="Manager")
        self.user_role = Role.objects.create(name="Employee")
        # Admin user
        self.admin = User.objects.create_user(username="admin", password="adminpass", is_staff=True)
        self.manager = User.objects.create_user(username="mgr", password="mgrpass")
        self.manager.roles.add(self.manager_role)
        self.emp = User.objects.create_user(username="emp", password="emppass", department=self.dept)
        self.emp.roles.add(self.user_role)

    def login_token(self, username, password):
        url = "/api/auth/login/"
        res = self.client.post(url, {"username": username, "password": password}, format="json")
        self.assertEqual(res.status_code, 200)
        return res.data["access"]

    def test_login_and_list_employees_requires_auth(self):
        # unauthorized
        res = self.client.get("/api/employees/")
        self.assertIn(res.status_code, (401, 403))
        # login
        token = self.login_token("admin", "adminpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.get("/api/employees/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data.get("data", {}))  # wrapped by middleware

    def test_employee_crud_as_manager(self):
        token = self.login_token("mgr", "mgrpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        # create
        res = self.client.post(
            "/api/employees/",
            {"username": "newguy", "password": "Newpass123!", "department_id": self.dept.id, "role_ids": [self.user_role.id]},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        eid = res.data.get("data", {}).get("id")
        # update
        res = self.client.patch(f"/api/employees/{eid}/", {"is_active": False}, format="json")
        self.assertEqual(res.status_code, 200)
        # assign roles
        res = self.client.post(f"/api/employees/{eid}/assign-roles/", {"role_ids": [self.manager_role.id]}, format="json")
        self.assertEqual(res.status_code, 200)

    def test_department_list_cached(self):
        token = self.login_token("admin", "adminpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res1 = self.client.get("/api/departments/")
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.get("/api/departments/")
        self.assertEqual(res2.status_code, 200)
from django.test import TestCase

# Create your tests here.

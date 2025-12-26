from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department, Role


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		("Organization", {"fields": ("department", "roles")}),
	)
	list_display = UserAdmin.list_display + ("department",)
	filter_horizontal = ("groups", "user_permissions", "roles")

from django.contrib import admin

# Register your models here.

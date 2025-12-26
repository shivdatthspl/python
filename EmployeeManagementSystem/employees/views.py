from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Employee, Department, Role
from .serializers import EmployeeSerializer, DepartmentSerializer, RoleSerializer
from .decorators import role_required
from .jwt_utils import generate_jwt


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # if request.user.is_staff or request.user.is_superuser:
        #     return True
        return request.user.roles.filter(name__in=["Admin", "Manager"]).exists()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department').prefetch_related('roles').all()
    serializer_class = EmployeeSerializer
    filterset_fields = ["is_active", "department", "roles", "username", "email"]
    ordering_fields = ["id", "username", "date_joined"]
    search_fields = ["username", "first_name", "last_name", "email"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "assign_roles"]:
            return [IsAdminOrManager()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="assign-roles")
    @role_required("Admin", "Manager")
    def assign_roles(self, request, pk=None):
        role_ids = request.data.get("role_ids", [])
        try:
            employee = self.get_queryset().get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.filter(id__in=role_ids)
        employee.roles.set(roles)
        employee.save()
        return Response(EmployeeSerializer(employee).data)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = ["name"]
    ordering_fields = ["id", "name"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrManager()]
        return [permissions.IsAuthenticated()]

    @method_decorator(cache_page(120))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_fields = ["name"]
    ordering_fields = ["id", "name"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrManager()]
        return [permissions.IsAuthenticated()]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if not user or not user.is_active:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    token = generate_jwt(user.id, user.username)
    return Response({"access": token})
from django.shortcuts import render

# Create your views here.

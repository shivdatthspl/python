from rest_framework import serializers
from .models import Employee, Department, Role


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all(), write_only=True, allow_null=True, required=False
    )
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        source="roles", queryset=Role.objects.all(), many=True, write_only=True, required=False
    )

    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Employee
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "department",
            "department_id",
            "roles",
            "role_ids",
        ]
        read_only_fields = ("is_staff", "date_joined", "last_login")

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        password = validated_data.pop("password", None)
        user = Employee(**validated_data)
        if password:
            user.set_password(password)
        else:
            # generate unusable if not provided; tests provide password
            user.set_unusable_password()
        user.save()
        if roles:
            user.roles.set(roles)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if roles is not None:
            instance.roles.set(roles)
        return instance

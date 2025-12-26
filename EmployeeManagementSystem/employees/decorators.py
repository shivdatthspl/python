from functools import wraps
from typing import Iterable
from rest_framework.response import Response
from rest_framework import status


def role_required(*allowed_roles: Iterable[str]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(view, request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            if user.is_superuser or user.is_staff:
                return view_func(view, request, *args, **kwargs)
            user_roles = set(user.roles.values_list("name", flat=True))
            if any(role in user_roles for role in allowed_roles):
                return view_func(view, request, *args, **kwargs)
            return Response({"detail": "Forbidden: insufficient role"}, status=status.HTTP_403_FORBIDDEN)

        return _wrapped

    return decorator

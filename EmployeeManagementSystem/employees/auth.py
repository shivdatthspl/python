from typing import Tuple, Optional
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from .jwt_utils import validate_jwt


User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        auth = authentication.get_authorization_header(request).decode('utf-8')
        if not auth:
            return None
        parts = auth.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed('Invalid Authorization header format')
        token = parts[1]
        validated = validate_jwt(token)
        if not validated:
            raise exceptions.AuthenticationFailed('Invalid or expired token')
        user_id, _ = validated
        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found or inactive')
        return user, None

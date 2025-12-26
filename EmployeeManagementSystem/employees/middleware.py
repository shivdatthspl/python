import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .jwt_utils import validate_jwt
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth.startswith('Bearer '):
            return None
        token = auth.split(' ', 1)[1].strip()
        validated = validate_jwt(token)
        if not validated:
            return None
        user_id, _ = validated
        try:
            request.user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            pass
        return None


class ApiEnvelopeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        # Timing headers
        try:
            elapsed_ms = int((time.perf_counter() - getattr(request, '_start_time', time.perf_counter())) * 1000)
            response['X-Response-Time-ms'] = str(elapsed_ms)
        except Exception:
            pass

        # Normalize JSON response structure for API paths
        path = getattr(request, 'path', '')
        # Do not wrap the auth login endpoint to keep response schema simple for clients/tests
        if path.startswith('/api/auth/login'):
            return response
        if path.startswith('/api/'):
            # If response is already a JsonResponse, attempt to wrap
            try:
                if hasattr(response, 'content') and 'application/json' in response.get('Content-Type', ''):
                    data = json.loads(response.content.decode('utf-8') or 'null')
                    ok = 200 <= getattr(response, 'status_code', 200) < 400
                    wrapped = {"success": ok, "data": data if ok else None, "error": None if ok else data}
                    drf_resp = Response(wrapped, status=response.status_code)
                    # Ensure the DRF Response is rendered so Django middleware can access content safely
                    drf_resp.accepted_renderer = JSONRenderer()
                    drf_resp.accepted_media_type = 'application/json'
                    drf_resp.renderer_context = {'request': request}
                    drf_resp.render()
                    return drf_resp
            except Exception:
                # Fail open: return original response
                return response
        return response

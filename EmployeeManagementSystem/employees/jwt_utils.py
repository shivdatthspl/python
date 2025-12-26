import datetime
from typing import Optional, Tuple

import jwt
from django.conf import settings


def generate_jwt(user_id: int, username: str) -> str:
    exp_minutes = settings.JWT_AUTH.get('EXP_MINUTES', 60)
    now = datetime.datetime.utcnow()
    payload = {
        'sub': str(user_id),
        'username': username,
        'iat': now,
        'exp': now + datetime.timedelta(minutes=exp_minutes),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_AUTH.get('ALGORITHM', 'HS256'))
    # pyjwt>=2 returns str
    return token


def validate_jwt(token: str) -> Optional[Tuple[int, dict]]:
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_AUTH.get('ALGORITHM', 'HS256')])
        return int(data['sub']), data
    except Exception:
        return None

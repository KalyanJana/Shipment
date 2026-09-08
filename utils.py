from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from learning.config import security_settings


def generate_access_token(data: dict, expiry: timedelta = timedelta(hours=1)) -> str:
   
    return jwt.encode(
        payload={
            **data,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + expiry
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM  # singular algorithm
    )

def decode_access_token(token: str)-> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token"
        )
    except jwt.PyJWTError:
        return None
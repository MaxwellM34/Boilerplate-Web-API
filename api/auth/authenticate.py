from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from auth.google import bearer, normalize_token, verify_google_token_db
from config import Config
from models import User

async def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> User:
    """Return an authenticated user or raise if the request is unauthorized."""
    if Config.OFFLINE_MODE:
        user, _ = await User.get_or_create(
            email=Config.OFFLINE_ADMIN_EMAIL,
            defaults={
                "firstname": "Dev",
                "lastname": "Admin",
                "is_admin": True,
                "disabled": False,
            },
        )

        needs_save = False
        if not user.is_admin:
            user.is_admin = True
            needs_save = True
        if user.disabled:
            user.disabled = False
            needs_save = True
        if needs_save:
            await user.save()
        return user

    token = normalize_token(credentials.credentials if credentials else None)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    user = await verify_google_token_db(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials",
        )

    return user


__all__ = ["authenticate"]

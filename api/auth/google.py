from __future__ import annotations

from typing import Optional

from fastapi.security import HTTPBearer

from config import Config
from models import User

try:
    from google.auth.transport.requests import Request as GoogleAuthRequest
    from google.oauth2 import id_token
except ImportError:  # pragma: no cover
    GoogleAuthRequest = None  # type: ignore[assignment]
    id_token = None  # type: ignore[assignment]

bearer = HTTPBearer(auto_error=False)


def normalize_token(raw_token: Optional[str]) -> Optional[str]:
    if not raw_token:
        return None
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        return token.split(None, 1)[1].strip()
    return token


def verify_google_token(token: str) -> Optional[str]:
    """Decode a Google token (if the package is installed) or fallback to debug mode."""
    if not token:
        return None

    if Config.DEBUG_AUTH and token == Config.SECRET_KEY:
        return Config.OFFLINE_ADMIN_EMAIL

    if id_token is None or GoogleAuthRequest is None:
        return None

    try:
        request = GoogleAuthRequest()
        decoded = id_token.verify_oauth2_token(token, request, Config.GOOGLE_AUDIENCE)
        email = decoded.get("email")
        if Config.DEBUG_AUTH:
            print(f"[auth] decoded token email={email!r}")
        return email if email else None
    except Exception as exc:  # pragma: no cover
        if Config.DEBUG_AUTH:
            print(f"[auth] google verification failed: {type(exc).__name__}: {exc}")
        return None


async def verify_google_token_db(token: str) -> Optional[User]:
    email = verify_google_token(token)
    if not email:
        return None

    user = await User.get_or_none(email__iexact=email)
    if not user:
        return None
    if user.disabled:
        return None
    return user


__all__ = ["bearer", "normalize_token", "verify_google_token", "verify_google_token_db"]

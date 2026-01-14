from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from auth.google import verify_google_token_payload
from config import Config
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])

UserOut = pydantic_model_creator(User, name="AuthUserOut")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserOut


class GoogleTokenRequest(BaseModel):
    id_token: str


def _google_firstname(email: str, claims: dict[str, Any]) -> str:
    given = (claims.get("given_name") or "").strip()
    if given:
        return given
    name = (claims.get("name") or "").strip()
    if name:
        return name.split()[0]
    return email.split("@", 1)[0]


def _google_lastname(claims: dict[str, Any]) -> str | None:
    family = (claims.get("family_name") or "").strip()
    if family:
        return family
    name = (claims.get("name") or "").strip()
    parts = name.split()
    if len(parts) > 1:
        return " ".join(parts[1:])
    return None


def _expires_in(claims: dict[str, Any]) -> int:
    exp = claims.get("exp")
    if not exp:
        return 0
    now = int(datetime.now(timezone.utc).timestamp())
    return max(0, int(exp) - now)


@router.post("/google", response_model=TokenResponse)
async def issue_google_token(payload: GoogleTokenRequest) -> TokenResponse:
    """Accept a Google ID token and return it as the API JWT."""
    if not Config.GOOGLE_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google audience is not configured",
        )
    claims = verify_google_token_payload(payload.id_token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google credentials",
        )
    email = claims.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email claim is missing",
        )

    user = await User.get_or_none(email__iexact=email)
    if not user:
        user = await User.create(
            email=email,
            firstname=_google_firstname(email, claims),
            lastname=_google_lastname(claims),
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )

    return TokenResponse(
        access_token=payload.id_token,
        token_type="bearer",
        expires_in=_expires_in(claims),
        user=await UserOut.from_tortoise_orm(user),
    )

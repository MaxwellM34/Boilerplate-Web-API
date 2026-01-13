from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from auth import authenticate
from models import User

router = APIRouter(prefix="/users", tags=["users"])

UserOut = pydantic_model_creator(User, name="UserOut")


class UserCreatePayload(BaseModel):
    email: str
    firstname: str
    lastname: str | None = None


class EmailPayload(BaseModel):
    email: str


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreatePayload):
    """Create a user unless the email is already taken."""
    if await User.filter(email__iexact=payload.email).exists():
        raise HTTPException(status_code=400, detail="User already exists")
    user = await User.create(
        email=payload.email,
        firstname=payload.firstname,
        lastname=payload.lastname,
    )
    return await UserOut.from_tortoise_orm(user)


@router.get("/", response_model=list[UserOut])
async def get_users(current_user: User = Depends(authenticate)):
    """List users. Requires authentication."""
    return await UserOut.from_queryset(User.all())


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_user(
    payload: EmailPayload, current_user: User = Depends(authenticate)
):
    deleted = await User.filter(email__iexact=payload.email).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return


@router.post("/adminize", response_model=UserOut)
async def promote_user(
    payload: EmailPayload, current_user: User = Depends(authenticate)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")

    user = await User.get_or_none(email__iexact=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    await user.save()
    return await UserOut.from_tortoise_orm(user)


@router.post("/deadminize", response_model=UserOut)
async def demote_user(
    payload: EmailPayload, current_user: User = Depends(authenticate)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")

    if current_user.email.lower() == payload.email.lower():
        raise HTTPException(
            status_code=400, detail="You cannot deadminize yourself"
        )

    user = await User.get_or_none(email__iexact=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = False
    await user.save()
    return await UserOut.from_tortoise_orm(user)

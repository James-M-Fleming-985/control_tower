from __future__ import annotations

"""Auth router — registration, login, refresh."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from epistemic_platform.database import get_db
from epistemic_platform.repositories.user_profile_repository import UserProfileRepository
from epistemic_platform.schemas.auth_schemas import LoginRequest, TokenResponse
from epistemic_platform.schemas.user_profile_schemas import UserProfileCreate, UserProfileRead

router = APIRouter()


@router.post("/register", response_model=UserProfileRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserProfileCreate, db: AsyncSession = Depends(get_db)):
    repo = UserProfileRepository(db)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    hashed = hash_password(data.password)
    user = await repo.create(data, hashed_password=hashed)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserProfileRepository(db)
    user = await repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = int(payload["sub"])
    repo = UserProfileRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )

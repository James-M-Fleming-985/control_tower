from __future__ import annotations

"""ConversationSession router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from epistemic_platform.schemas.conversation_session_schemas import (
    ConversationSessionCreate,
    ConversationSessionRead,
    ConversationSessionSummary,
    ConversationSessionUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ConversationSessionSummary])
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    return await repo.list_by_user(user.id, skip=skip, limit=limit)


@router.get("/active", response_model=list[ConversationSessionSummary])
async def list_active_sessions(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    return await repo.list_active(user.id)


@router.get("/{session_id}", response_model=ConversationSessionRead)
async def get_session(
    session_id: int,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    session = await repo.get(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("/", response_model=ConversationSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: ConversationSessionCreate,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    return await repo.create(user.id, data)


@router.patch("/{session_id}", response_model=ConversationSessionRead)
async def update_session(
    session_id: int,
    data: ConversationSessionUpdate,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    session = await repo.get(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    updated = await repo.update(session_id, data)
    return updated


@router.post("/{session_id}/end", response_model=ConversationSessionRead)
async def end_session(
    session_id: int,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    session = await repo.get(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    ended = await repo.end_session(session_id)
    return ended


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationSessionRepository(db)
    session = await repo.get(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    await repo.delete(session_id)

"""Admin-only route guard."""

from fastapi import Depends, HTTPException, status

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.models.user_profile import UserProfile


async def require_admin(
    user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """Dependency that requires the authenticated user to have admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user

from __future__ import annotations
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.services import collaboration as collaboration_service
from models import AcceptInviteResponse

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])


@router.post("/invites/{token}/accept", response_model=AcceptInviteResponse)
async def accept_invite(
    token: str,
    user_id: str = Depends(get_current_user),
):
    return await collaboration_service.accept_invite(token, user_id)

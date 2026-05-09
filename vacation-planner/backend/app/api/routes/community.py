from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends

from app.core.security import get_current_user, get_optional_user
from app.services import community as community_service
from models import CommunityItinerary

router = APIRouter(prefix="/api/community", tags=["community"])


@router.get("/feed", response_model=list[CommunityItinerary])
async def get_community_feed(
    sort_by: str = "likes",
    user_id: Optional[str] = Depends(get_optional_user),
):
    return await community_service.get_community_feed(sort_by, user_id)


@router.post("/like/{itinerary_id}")
async def toggle_like(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await community_service.toggle_like(itinerary_id, user_id)


@router.post("/fork/{itinerary_id}")
async def fork_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await community_service.fork_itinerary(itinerary_id, user_id)

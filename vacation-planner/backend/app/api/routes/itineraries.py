from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services import collaboration as collaboration_service
from app.services import itineraries as itinerary_service
from app.services import reactions as reaction_service
from models import (
    ActivityReactionRequest,
    ActivityReactionSummary,
    CollaborationState,
    CreateInviteRequest,
    InviteResponse,
    ItineraryUpdate,
    VoteRequest,
)

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])


class SaveItineraryRequest(BaseModel):
    title: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_public: bool = False
    ai_data: dict


@router.post("/save")
async def save_itinerary(
    payload: SaveItineraryRequest,
    user_id: str = Depends(get_current_user),
):
    return await itinerary_service.save_itinerary(payload, user_id)


@router.get("/me")
async def get_my_itineraries(user_id: str = Depends(get_current_user)):
    return await itinerary_service.get_my_itineraries(user_id)


@router.get("/{itinerary_id}")
async def get_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await itinerary_service.get_itinerary(itinerary_id, user_id)


@router.patch("/{itinerary_id}")
async def update_itinerary(
    itinerary_id: str,
    update_data: ItineraryUpdate,
    user_id: str = Depends(get_current_user),
):
    return await itinerary_service.update_itinerary(itinerary_id, update_data, user_id)


@router.post("/{itinerary_id}/vote-regenerate")
async def vote_regenerate(
    itinerary_id: str,
    vote_req: VoteRequest,
    bg_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
):
    return await collaboration_service.vote_regenerate(itinerary_id, vote_req, bg_tasks, user_id)


@router.get("/{itinerary_id}/reactions", response_model=list[ActivityReactionSummary])
async def get_activity_reactions(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await reaction_service.get_activity_reactions(itinerary_id, user_id)


@router.post("/{itinerary_id}/reactions/toggle")
async def toggle_activity_reaction(
    itinerary_id: str,
    payload: ActivityReactionRequest,
    user_id: str = Depends(get_current_user),
):
    return await reaction_service.toggle_activity_reaction(itinerary_id, payload, user_id)


@router.delete("/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await itinerary_service.delete_itinerary(itinerary_id, user_id)


@router.get("/{itinerary_id}/collaboration", response_model=CollaborationState)
async def get_collaboration_state(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    return await collaboration_service.get_collaboration_state(itinerary_id, user_id)


@router.post("/{itinerary_id}/collaboration/invites", response_model=InviteResponse)
async def create_invite(
    itinerary_id: str,
    payload: CreateInviteRequest,
    user_id: str = Depends(get_current_user),
):
    return await collaboration_service.create_invite(itinerary_id, payload, user_id)


@router.delete("/{itinerary_id}/collaboration/collaborators/{collaborator_user_id}")
async def remove_collaborator(
    itinerary_id: str,
    collaborator_user_id: str,
    user_id: str = Depends(get_current_user),
):
    return await collaboration_service.remove_collaborator(itinerary_id, collaborator_user_id, user_id)

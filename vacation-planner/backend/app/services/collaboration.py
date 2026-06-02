from __future__ import annotations
from datetime import datetime, timedelta, timezone
import json
import math
import secrets

from fastapi import BackgroundTasks, HTTPException
from loguru import logger

from agent_regenerate import regenerate_single_activity
from app.db.supabase import require_supabase
from models import (
    AcceptInviteResponse,
    ActivityVote,
    CollaborationState,
    Collaborator,
    CreateInviteRequest,
    InviteResponse,
    VoteRequest,
)


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    text = str(exc)
    return "PGRST205" in text and table_name in text


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _vote_key(day_index: int, activity_index: int) -> str:
    return f"day_{day_index}_act_{activity_index}"


def _user_name_from_id(user_id: str) -> str:
    return f"Traveler {user_id[:8]}"


def _select_trip(db, itinerary_id: str) -> dict:
    result = (
        db.table("itineraries")
        .select("id, user_id, title, destination, start_date, end_date, is_public, created_at, ai_data")
        .eq("id", itinerary_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Itinerary not found.")
    return result.data[0]


def _collaborator_rows(db, itinerary_id: str) -> list[dict]:
    try:
        result = (
            db.table("trip_collaborators")
            .select("user_id, role, joined_at, profiles!trip_collaborators_user_id_fkey(display_name, avatar_url)")
            .eq("itinerary_id", itinerary_id)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        if _is_missing_table_error(exc, "trip_collaborators"):
            logger.warning("[DB] trip_collaborators table is missing; collaboration features are disabled.")
            return []
        raise


def _collaborator_role(db, itinerary_id: str, user_id: str) -> str | None:
    try:
        result = (
            db.table("trip_collaborators")
            .select("role")
            .eq("itinerary_id", itinerary_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "trip_collaborators"):
            logger.warning("[DB] trip_collaborators table is missing; treating user as non-collaborator.")
            return None
        raise
    if not result.data:
        return None
    return result.data[0].get("role") or "viewer"


def get_user_role(db, trip: dict, user_id: str) -> str | None:
    if trip.get("user_id") == user_id:
        return "owner"
    collaborator_role = _collaborator_role(db, trip["id"], user_id)
    if collaborator_role:
        return collaborator_role
    if trip.get("is_public"):
        return "public"
    return "link_viewer"


def require_trip_access(db, itinerary_id: str, user_id: str) -> tuple[dict, str]:
    trip = _select_trip(db, itinerary_id)
    role = get_user_role(db, trip, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="You do not have access to this itinerary.")
    return trip, role


def require_edit_access(db, itinerary_id: str, user_id: str) -> tuple[dict, str]:
    trip, role = require_trip_access(db, itinerary_id, user_id)
    if role not in {"owner", "editor"}:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this itinerary.")
    return trip, role


def require_owner(db, itinerary_id: str, user_id: str) -> dict:
    trip = _select_trip(db, itinerary_id)
    if trip.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Only the trip owner can do this.")
    return trip


def _format_collaborator(row: dict) -> Collaborator:
    profile = row.get("profiles") or {}
    return Collaborator(
        user_id=row["user_id"],
        role=row.get("role") or "viewer",
        display_name=profile.get("display_name"),
        avatar_url=profile.get("avatar_url"),
        joined_at=row.get("joined_at"),
    )


def _vote_rows(db, itinerary_id: str) -> list[dict]:
    try:
        result = (
            db.table("activity_votes")
            .select("day_index, activity_index, user_id, voter_name, voter_avatar_id, created_at")
            .eq("itinerary_id", itinerary_id)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        if _is_missing_table_error(exc, "activity_votes"):
            logger.warning("[DB] activity_votes table is missing; regenerate votes are disabled.")
            return []
        raise


def _eligible_voter_count(db, trip: dict) -> int:
    collaborator_ids = {
        row["user_id"]
        for row in _collaborator_rows(db, trip["id"])
        if row.get("role") in {"viewer", "editor"}
    }
    collaborator_ids.discard(trip["user_id"])
    return 1 + len(collaborator_ids)


def _majority_threshold(eligible_voters: int) -> int:
    return max(1, math.ceil(eligible_voters / 2))


async def get_collaboration_state(itinerary_id: str, user_id: str) -> CollaborationState:
    db = require_supabase()
    trip, role = require_trip_access(db, itinerary_id, user_id)
    collaborators = [_format_collaborator(row) for row in _collaborator_rows(db, itinerary_id)]
    votes = [ActivityVote(**row) for row in _vote_rows(db, itinerary_id)]
    can_edit = role in {"owner", "editor"}

    return CollaborationState(
        itinerary_id=itinerary_id,
        role=role,
        can_edit=can_edit,
        can_invite=role == "owner",
        eligible_voters=_eligible_voter_count(db, trip),
        collaborators=collaborators,
        votes=votes,
    )


async def create_invite(itinerary_id: str, payload: CreateInviteRequest, user_id: str) -> InviteResponse:
    db = require_supabase()
    require_owner(db, itinerary_id, user_id)
    expires_at = _now() + timedelta(days=payload.expires_in_days)
    token = secrets.token_urlsafe(24)

    result = db.table("trip_invites").insert(
        {
            "itinerary_id": itinerary_id,
            "token": token,
            "role": payload.role,
            "created_by": user_id,
            "expires_at": expires_at.isoformat(),
        }
    ).execute()
    invite = result.data[0]
    return InviteResponse(token=invite["token"], role=invite["role"], expires_at=invite["expires_at"])


async def accept_invite(token: str, user_id: str) -> AcceptInviteResponse:
    db = require_supabase()
    result = db.table("trip_invites").select("*").eq("token", token).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Invite not found.")

    invite = result.data[0]
    expires_at = datetime.fromisoformat(str(invite["expires_at"]).replace("Z", "+00:00"))
    if expires_at < _now():
        raise HTTPException(status_code=410, detail="Invite has expired.")

    trip = _select_trip(db, invite["itinerary_id"])
    if trip["user_id"] != user_id:
        existing = (
            db.table("trip_collaborators")
            .select("user_id")
            .eq("itinerary_id", invite["itinerary_id"])
            .eq("user_id", user_id)
            .execute()
        )
        payload = {
            "itinerary_id": invite["itinerary_id"],
            "user_id": user_id,
            "role": invite["role"],
            "invited_by": invite["created_by"],
            "joined_at": _now().isoformat(),
        }
        if existing.data:
            db.table("trip_collaborators").update(payload).eq("itinerary_id", invite["itinerary_id"]).eq("user_id", user_id).execute()
        else:
            db.table("trip_collaborators").insert(payload).execute()

    db.table("trip_invites").update({"accepted_at": _now().isoformat()}).eq("token", token).execute()
    return AcceptInviteResponse(itinerary_id=invite["itinerary_id"], role=invite["role"])


async def remove_collaborator(itinerary_id: str, collaborator_user_id: str, user_id: str) -> dict:
    db = require_supabase()
    require_owner(db, itinerary_id, user_id)
    db.table("trip_collaborators").delete().eq("itinerary_id", itinerary_id).eq("user_id", collaborator_user_id).execute()
    return {"status": "removed"}


async def _bg_regenerate_from_vote(itinerary_id: str, vote_req: VoteRequest, current_ai_data: dict, current_trip: dict):
    db = require_supabase()
    vote_key = _vote_key(vote_req.day_index, vote_req.activity_index)

    try:
        current_ai_data.setdefault("regenerating_keys", {})
        current_ai_data["regenerating_keys"][vote_key] = True
        db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()

        day_obj = current_ai_data["experience"]["itinerary"][vote_req.day_index]
        old_act = day_obj["activities"][vote_req.activity_index]
        day_context = json.dumps([a["title"] for i, a in enumerate(day_obj["activities"]) if i != vote_req.activity_index])
        destination = current_trip.get("destination", "Unknown")
        vibe_summary = current_ai_data["experience"].get("vibe_summary", "")

        new_act = await regenerate_single_activity(vibe_summary, day_context, destination, json.dumps(old_act))
        current_ai_data["experience"]["itinerary"][vote_req.day_index]["activities"][vote_req.activity_index] = new_act.model_dump()

        current_ai_data.get("regenerating_keys", {}).pop(vote_key, None)
        db.table("activity_votes").delete().eq("itinerary_id", itinerary_id).eq("day_index", vote_req.day_index).eq("activity_index", vote_req.activity_index).execute()
        db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()
        logger.info(f"Regeneration complete for {vote_key} on itinerary {itinerary_id}")

    except Exception as e:
        logger.error(f"Background regeneration failed: {e}")
        current_ai_data.get("regenerating_keys", {}).pop(vote_key, None)
        db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()


async def vote_regenerate(
    itinerary_id: str,
    vote_req: VoteRequest,
    bg_tasks: BackgroundTasks,
    user_id: str,
) -> dict:
    db = require_supabase()
    trip, role = require_trip_access(db, itinerary_id, user_id)
    if role == "public":
        raise HTTPException(status_code=403, detail="Join the trip before voting.")

    ai_data = trip.get("ai_data", {})
    vote_key = _vote_key(vote_req.day_index, vote_req.activity_index)
    if ai_data.get("regenerating_keys", {}).get(vote_key) is True:
        return {"status": "already_regenerating"}

    voter_name = vote_req.voter.name if vote_req.voter else _user_name_from_id(user_id)
    voter_avatar_id = vote_req.voter.avatarId if vote_req.voter else None
    existing = (
        db.table("activity_votes")
        .select("user_id")
        .eq("itinerary_id", itinerary_id)
        .eq("day_index", vote_req.day_index)
        .eq("activity_index", vote_req.activity_index)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        db.table("activity_votes").insert(
            {
                "itinerary_id": itinerary_id,
                "day_index": vote_req.day_index,
                "activity_index": vote_req.activity_index,
                "user_id": user_id,
                "voter_name": voter_name,
                "voter_avatar_id": voter_avatar_id,
            }
        ).execute()

    votes_for_activity = (
        db.table("activity_votes")
        .select("user_id")
        .eq("itinerary_id", itinerary_id)
        .eq("day_index", vote_req.day_index)
        .eq("activity_index", vote_req.activity_index)
        .execute()
    )
    vote_count = len({vote["user_id"] for vote in votes_for_activity.data or []})
    eligible_voters = max(_eligible_voter_count(db, trip), vote_req.total_online or 1)
    threshold = _majority_threshold(eligible_voters)

    if vote_count >= threshold:
        ai_data.setdefault("regenerating_keys", {})
        ai_data["regenerating_keys"][vote_key] = True
        db.table("itineraries").update({"ai_data": ai_data}).eq("id", itinerary_id).execute()
        bg_tasks.add_task(_bg_regenerate_from_vote, itinerary_id, vote_req, ai_data, trip)
        return {
            "status": "regeneration_started",
            "votes_count": vote_count,
            "eligible_voters": eligible_voters,
            "threshold": threshold,
        }

    return {
        "status": "vote_recorded",
        "votes_count": vote_count,
        "eligible_voters": eligible_voters,
        "threshold": threshold,
    }

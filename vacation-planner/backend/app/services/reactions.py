from __future__ import annotations
from collections import defaultdict

from fastapi import HTTPException
from loguru import logger

from app.db.supabase import require_supabase
from app.services.collaboration import require_trip_access
from models import ActivityReactionRequest, ActivityReactionSummary


def _is_missing_reactions_table(exc: Exception) -> bool:
    text = str(exc)
    return "PGRST205" in text and "activity_reactions" in text


def _reaction_rows(db, itinerary_id: str) -> list[dict]:
    try:
        result = (
            db.table("activity_reactions")
            .select("day_index, activity_index, reaction_type, user_id")
            .eq("itinerary_id", itinerary_id)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        if _is_missing_reactions_table(exc):
            logger.warning("[DB] activity_reactions table is missing; reactions are disabled.")
            return []
        raise


def _summarize_reactions(rows: list[dict], user_id: str) -> list[ActivityReactionSummary]:
    counts: dict[tuple[int, int, str], set[str]] = defaultdict(set)
    reacted_by_me: set[tuple[int, int, str]] = set()

    for row in rows:
        key = (
            int(row["day_index"]),
            int(row["activity_index"]),
            row["reaction_type"],
        )
        counts[key].add(row["user_id"])
        if row["user_id"] == user_id:
            reacted_by_me.add(key)

    return [
        ActivityReactionSummary(
            day_index=day_index,
            activity_index=activity_index,
            reaction_type=reaction_type,
            count=len(user_ids),
            reacted_by_me=key in reacted_by_me,
        )
        for key, user_ids in sorted(counts.items())
        for day_index, activity_index, reaction_type in [key]
    ]


async def get_activity_reactions(itinerary_id: str, user_id: str) -> list[ActivityReactionSummary]:
    db = require_supabase()
    require_trip_access(db, itinerary_id, user_id)
    return _summarize_reactions(_reaction_rows(db, itinerary_id), user_id)


async def toggle_activity_reaction(
    itinerary_id: str,
    payload: ActivityReactionRequest,
    user_id: str,
) -> dict:
    db = require_supabase()
    require_trip_access(db, itinerary_id, user_id)

    try:
        existing = (
            db.table("activity_reactions")
            .select("user_id")
            .eq("itinerary_id", itinerary_id)
            .eq("day_index", payload.day_index)
            .eq("activity_index", payload.activity_index)
            .eq("reaction_type", payload.reaction_type)
            .eq("user_id", user_id)
            .execute()
        )

        if existing.data:
            (
                db.table("activity_reactions")
                .delete()
                .eq("itinerary_id", itinerary_id)
                .eq("day_index", payload.day_index)
                .eq("activity_index", payload.activity_index)
                .eq("reaction_type", payload.reaction_type)
                .eq("user_id", user_id)
                .execute()
            )
            status = "removed"
        else:
            db.table("activity_reactions").insert(
                {
                    "itinerary_id": itinerary_id,
                    "day_index": payload.day_index,
                    "activity_index": payload.activity_index,
                    "reaction_type": payload.reaction_type,
                    "user_id": user_id,
                }
            ).execute()
            status = "added"

        return {
            "status": status,
            "reactions": await get_activity_reactions(itinerary_id, user_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        if _is_missing_reactions_table(e):
            raise HTTPException(
                status_code=503,
                detail="Activity reactions table is missing. Run the Supabase schema migration first.",
            )
        logger.error(f"[Reactions] Toggle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

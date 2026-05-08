from fastapi import HTTPException
from loguru import logger

from app.db.supabase import require_supabase
from models import CommunityItinerary


async def get_community_feed(sort_by: str, user_id: str | None) -> list[CommunityItinerary]:
    db = require_supabase()

    try:
        query = (
            db.table("itineraries")
            .select("*, profiles!itineraries_user_id_fkey(display_name, avatar_url)")
            .eq("is_public", True)
        )

        if sort_by == "likes":
            query = query.order("likes_count", desc=True)
        else:
            query = query.order("created_at", desc=True)

        result = query.limit(50).execute()

        user_likes = set()
        if user_id:
            likes_res = db.table("itinerary_likes").select("itinerary_id").eq("user_id", user_id).execute()
            user_likes = {like["itinerary_id"] for like in likes_res.data}

        feed_items = []
        for item in result.data:
            profile = item.get("profiles", {})
            feed_items.append(
                CommunityItinerary(
                    id=item["id"],
                    user_id=item["user_id"],
                    title=item["title"],
                    destination=item["destination"],
                    start_date=item.get("start_date"),
                    end_date=item.get("end_date"),
                    likes_count=item.get("likes_count", 0),
                    forks_count=item.get("forks_count", 0),
                    is_public=item["is_public"],
                    created_at=item["created_at"],
                    ai_data=item["ai_data"],
                    author_name=profile.get("display_name", "Unknown"),
                    author_avatar=profile.get("avatar_url"),
                    is_liked_by_me=item["id"] in user_likes,
                )
            )

        return feed_items

    except Exception as e:
        logger.error(f"[Community] Feed failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def toggle_like(itinerary_id: str, user_id: str) -> dict:
    db = require_supabase()

    try:
        existing = (
            db.table("itinerary_likes")
            .select("*")
            .eq("user_id", user_id)
            .eq("itinerary_id", itinerary_id)
            .execute()
        )

        if existing.data:
            db.table("itinerary_likes").delete().eq("user_id", user_id).eq("itinerary_id", itinerary_id).execute()

            res = db.table("itineraries").select("likes_count").eq("id", itinerary_id).execute()
            new_count = max(0, (res.data[0].get("likes_count") or 0) - 1)
            db.table("itineraries").update({"likes_count": new_count}).eq("id", itinerary_id).execute()

            return {"status": "unliked", "likes_count": new_count}

        db.table("itinerary_likes").insert(
            {
                "user_id": user_id,
                "itinerary_id": itinerary_id,
            }
        ).execute()

        res = db.table("itineraries").select("likes_count").eq("id", itinerary_id).execute()
        new_count = (res.data[0].get("likes_count") or 0) + 1
        db.table("itineraries").update({"likes_count": new_count}).eq("id", itinerary_id).execute()

        return {"status": "liked", "likes_count": new_count}

    except Exception as e:
        logger.error(f"[Community] Like toggle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def fork_itinerary(itinerary_id: str, user_id: str) -> dict:
    db = require_supabase()

    try:
        source_res = db.table("itineraries").select("*").eq("id", itinerary_id).execute()
        if not source_res.data:
            raise HTTPException(status_code=404, detail="Itinerary not found.")

        source = source_res.data[0]
        new_itinerary = {
            "user_id": user_id,
            "title": f"{source['title']} (Copy)",
            "destination": source["destination"],
            "start_date": source.get("start_date"),
            "end_date": source.get("end_date"),
            "is_public": False,
            "ai_data": source["ai_data"],
            "likes_count": 0,
            "forks_count": 0,
        }

        clone_res = db.table("itineraries").insert(new_itinerary).execute()

        new_forks_count = (source.get("forks_count") or 0) + 1
        db.table("itineraries").update({"forks_count": new_forks_count}).eq("id", itinerary_id).execute()

        logger.info(f"[Community] User {user_id} forked itinerary {itinerary_id}")
        return {"status": "forked", "new_id": clone_res.data[0]["id"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Community] Fork failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

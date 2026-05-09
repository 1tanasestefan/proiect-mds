from __future__ import annotations
from fastapi import HTTPException
from loguru import logger
from supabase import Client, create_client

from app.core.config import get_settings

settings = get_settings()

SUPABASE_URL: str = settings.supabase_url
SUPABASE_KEY: str = settings.supabase_key

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_KEY not set in .env - database features will be disabled.")

supabase: Client | None = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def get_supabase() -> Client | None:
    return supabase


def require_supabase() -> Client:
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")
    return supabase

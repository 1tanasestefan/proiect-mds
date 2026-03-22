"""
Supabase client initialization.
Reads SUPABASE_URL and SUPABASE_KEY from .env
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # This is the anon/public key

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_KEY not set in .env — database features will be disabled.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None  # type: ignore

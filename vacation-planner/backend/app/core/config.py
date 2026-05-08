import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_title: str = "AI Travel Planner Backend (Zero-Cost Stack)"
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    )
    local_llm_base_url: str = "http://localhost:11434"
    local_llm_model: str = "llama3.1:8b"
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_jwt_secret: str = ""
    port: int = 8000


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@lru_cache
def get_settings() -> Settings:
    cors_origins = _split_csv(os.getenv("CORS_ORIGINS", ""))
    return Settings(
        cors_origins=cors_origins or Settings.cors_origins,
        local_llm_base_url=os.getenv("LOCAL_LLM_BASE_URL", Settings.local_llm_base_url),
        local_llm_model=os.getenv("LOCAL_LLM_MODEL", Settings.local_llm_model),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        port=int(os.getenv("PORT", Settings.port)),
    )

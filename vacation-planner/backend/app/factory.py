from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import collaboration, community, geocoding, health, itineraries, planning
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_title)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(geocoding.router)
    app.include_router(planning.router)
    app.include_router(itineraries.router)
    app.include_router(community.router)
    app.include_router(collaboration.router)

    return app

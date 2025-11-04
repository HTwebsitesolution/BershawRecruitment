from __future__ import annotations
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ingest, normalize, endorsement, tone, outreach

# Configure logging for intent classification review
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Recruit Assist API",
        version="0.1.0",
        description="Skeleton API for CV ingest, JD normalization, and endorsement generation."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingest.router)
    app.include_router(normalize.router)
    app.include_router(endorsement.router)
    app.include_router(tone.router)
    app.include_router(outreach.router)

    @app.get("/healthz")
    async def health():
        return {"ok": True}

    return app

app = create_app()


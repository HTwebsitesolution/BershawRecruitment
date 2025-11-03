from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ingest, normalize, endorsement

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

    @app.get("/healthz")
    async def health():
        return {"ok": True}

    return app

app = create_app()


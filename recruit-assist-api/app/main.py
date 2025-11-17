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

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Recruit Assist API",
            "version": "0.1.0",
            "description": "AI-powered recruiting platform API for CV parsing, JD normalization, and endorsement generation.",
            "docs": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "endpoints": {
                "health": "/healthz",
                "ingest": {
                    "cv_upload": "POST /ingest/cv?use_llm=true"
                },
                "normalize": {
                    "jd": "POST /normalize/jd?use_llm=true"
                },
                "endorsement": {
                    "generate": "POST /endorsement/generate?use_llm=true"
                },
                "outreach": {
                    "draft_connect": "POST /outreach/draft/connect?mode=llm",
                    "draft_after_accept": "POST /outreach/draft/after-accept",
                    "route_reply": "POST /outreach/route-reply"
                },
                "tone": {
                    "get": "GET /tone",
                    "update": "POST /tone"
                }
            },
            "status": "running"
        }

    @app.get("/healthz")
    async def health():
        return {"ok": True}

    return app

app = create_app()


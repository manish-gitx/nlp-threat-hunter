import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import chat, entities, ingest, reports, stats, threats

logger = logging.getLogger("threat-hunter")
logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingest.router)
    app.include_router(threats.router)
    app.include_router(stats.router)
    app.include_router(reports.router)
    app.include_router(chat.router)
    app.include_router(entities.router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()
        # Warm up the classifier so the first request isn't slow.
        from app.nlp.classifier import get_classifier
        get_classifier()
        logger.info("Threat Hunter API ready.")

    @app.get("/health")
    def health():
        return {"status": "ok", "app": settings.app_name}

    @app.get("/")
    def root():
        return {
            "app": settings.app_name,
            "docs": "/docs",
            "endpoints": [
                "/api/ingest",
                "/api/ingest/bulk",
                "/api/ingest/analyze",
                "/api/threats",
                "/api/stats",
                "/api/reports/generate",
                "/api/chat",
                "/api/entities",
                "/api/entities/iocs",
            ],
        }

    return app


app = create_app()

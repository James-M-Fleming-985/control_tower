import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from epistemic_platform import __version__
from epistemic_platform.config import get_settings

# Configure root logger so ALL application loggers emit to stdout/stderr
# (visible in Railway deploy logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
# Silence noisy libraries
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

_PACKAGE_DIR = Path(__file__).resolve().parent

# Build info — commit hash from Railway, timestamp from app startup
_commit = os.getenv("RAILWAY_GIT_COMMIT_SHA", "")
GIT_COMMIT = _commit[:7] if _commit else "unknown"
DEPLOY_TIMESTAMP = datetime.utcnow().isoformat()
BUILD_VERSION = f"{__version__}-{GIT_COMMIT}"


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-driven communication development platform using epistemological reasoning",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files — only mount if directory exists
    static_dir = _PACKAGE_DIR / "static"
    if static_dir.is_dir():
        from fastapi.staticfiles import StaticFiles
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Root route — SPA when frontend is built, else Coming Soon landing page
    frontend_dist = _PACKAGE_DIR / "frontend" / "dist"
    spa_index = frontend_dist / "index.html"

    if spa_index.is_file():
        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        async def root_page():
            return FileResponse(str(spa_index))
    else:
        templates_dir = _PACKAGE_DIR / "templates"
        if templates_dir.is_dir():
            from fastapi.templating import Jinja2Templates
            _templates = Jinja2Templates(directory=str(templates_dir))

            @app.get("/", response_class=HTMLResponse, include_in_schema=False)
            async def landing_page(request: Request):
                return _templates.TemplateResponse(
                    "landing.html", {
                        "request": request,
                        "app_name": settings.app_name,
                        "version": BUILD_VERSION,
                        "git_commit": GIT_COMMIT,
                        "deploy_timestamp": DEPLOY_TIMESTAMP,
                    }
                )

    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "ok",
            "version": BUILD_VERSION,
            "git_commit": GIT_COMMIT,
            "deploy_timestamp": DEPLOY_TIMESTAMP,
            "app": settings.app_name,
        }

    @app.get(f"{settings.api_prefix}/client-config", tags=["config"])
    async def client_config():
        """Public config values the frontend needs at runtime."""
        return {
            "avatar_service_url": settings.avatar_service_url or None,
        }

    @app.get("/health/db", tags=["health"])
    async def db_health_check():
        """Diagnostic: check DB connection, migration status, and schema."""
        from sqlalchemy import text as sa_text
        from epistemic_platform.database import async_session_factory

        info: dict = {"status": "checking"}
        try:
            async with async_session_factory() as db:
                try:
                    row = (await db.execute(sa_text("SELECT version_num FROM alembic_version"))).fetchone()
                    info["alembic_version"] = row[0] if row else "no rows"
                except Exception as exc:
                    info["alembic_version"] = f"error: {exc}"

                try:
                    await db.execute(sa_text("SELECT xp, level, achievements, subscription_tier FROM user_profiles LIMIT 0"))
                    info["gamification_columns"] = "present"
                except Exception:
                    info["gamification_columns"] = "MISSING"

                try:
                    await db.execute(sa_text("SELECT parent_session_id FROM conversation_sessions LIMIT 0"))
                    info["parent_session_id_column"] = "present"
                except Exception:
                    info["parent_session_id_column"] = "MISSING"

                try:
                    row = (await db.execute(sa_text("SELECT count(*) FROM actor_profiles"))).fetchone()
                    info["actor_count"] = row[0] if row else 0
                except Exception as exc:
                    info["actor_count"] = f"error: {exc}"

                try:
                    row = (await db.execute(sa_text(
                        "SELECT count(*) FROM actor_profiles WHERE ontology_config::text LIKE '%voice_id%'"
                    ))).fetchone()
                    info["actors_with_voice_id"] = row[0] if row else 0
                except Exception as exc:
                    info["actors_with_voice_id"] = f"error: {exc}"

                info["status"] = "ok"
        except Exception as exc:
            info["status"] = f"error: {exc}"

        return info

    favicon_path = _PACKAGE_DIR / "static" / "favicon.ico"
    if favicon_path.is_file():
        @app.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            return FileResponse(str(favicon_path))

    manifest_path = _PACKAGE_DIR / "static" / "manifest.json"
    if manifest_path.is_file():
        @app.get("/manifest.json", include_in_schema=False)
        async def manifest():
            return FileResponse(str(manifest_path), media_type="application/manifest+json")

    _register_routers(app)
    _register_events(app)

    # SPA frontend — serve built React app from frontend/dist
    if frontend_dist.is_dir():
        from fastapi.staticfiles import StaticFiles

        # Mount assets directory for JS/CSS/images
        assets_dir = frontend_dist / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(request: Request, full_path: str):
            # Don't catch API, WS, health, or static paths
            if full_path.startswith(("api/", "ws/", "health", "static/", "favicon.ico", "manifest.json")):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            # Serve actual files from dist if they exist
            file_path = frontend_dist / full_path
            if file_path.is_file() and frontend_dist in file_path.resolve().parents:
                return FileResponse(str(file_path))
            # SPA fallback — serve index.html
            if spa_index.is_file():
                return FileResponse(str(spa_index))
            return JSONResponse(status_code=404, content={"detail": "Not found"})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}\n{''.join(tb)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__},
        )

    return app


def _register_routers(app: FastAPI) -> None:
    from epistemic_platform.routers import (
        actor_profile_router,
        user_profile_router,
        conversation_session_router,
        scenario_definition_router,
        auth_router,
        websocket_router,
        voice_websocket_router,
        assessment_router,
        gamification_router,
        analytics_router,
        debrief_websocket_router,
    )

    prefix = get_settings().api_prefix
    app.include_router(auth_router.router, prefix=f"{prefix}/auth", tags=["auth"])
    app.include_router(actor_profile_router.router, prefix=f"{prefix}/actors", tags=["actors"])
    app.include_router(user_profile_router.router, prefix=f"{prefix}/users", tags=["users"])
    app.include_router(
        conversation_session_router.router, prefix=f"{prefix}/sessions", tags=["sessions"]
    )
    app.include_router(
        scenario_definition_router.router, prefix=f"{prefix}/scenarios", tags=["scenarios"]
    )
    app.include_router(
        assessment_router.router, prefix=f"{prefix}/assessment", tags=["assessment"]
    )
    app.include_router(
        gamification_router.router, prefix=f"{prefix}/gamification", tags=["gamification"]
    )
    app.include_router(
        analytics_router.router, prefix=f"{prefix}/analytics", tags=["analytics"]
    )
    # WebSocket endpoints (no prefix — mounted at /ws/...)
    app.include_router(websocket_router.router, tags=["websocket"])
    app.include_router(voice_websocket_router.router, tags=["voice-websocket"])
    app.include_router(debrief_websocket_router.router, tags=["debrief-websocket"])


def _register_events(app: FastAPI) -> None:
    @app.on_event("startup")
    async def on_startup():
        import logging
        logger = logging.getLogger(__name__)
        try:
            from epistemic_platform.database import async_session_factory, engine, Base
            # Import all models so Base.metadata is complete
            from epistemic_platform.models import actor_profile, user_profile, conversation_session, scenario_definition  # noqa: F401

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async with async_session_factory() as session:
                from epistemic_platform.ontology.seed_loader import load_seed_actors, load_seed_scenarios
                await load_seed_actors(session)
                await load_seed_scenarios(session)
                await session.commit()
            logger.info("Database initialized and seed data loaded")
        except Exception as e:
            logger.error(f"Startup DB initialization failed: {e}")
            logger.error("App will start but database features may not work")

    @app.on_event("shutdown")
    async def on_shutdown():
        from epistemic_platform.database import engine
        from epistemic_platform.engine.connection_manager import manager

        await manager.shutdown()
        await engine.dispose()


app = create_app()

import logging
import os
import traceback
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from epistemic_platform import __version__
from epistemic_platform.config import get_settings

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

    # Landing page — only if templates directory exists
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

    favicon_path = _PACKAGE_DIR / "static" / "favicon.ico"
    if favicon_path.is_file():
        @app.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            return FileResponse(str(favicon_path))

    _register_routers(app)
    _register_events(app)

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
    # WebSocket endpoint (no prefix — mounted at /ws/conversation/{session_id})
    app.include_router(websocket_router.router, tags=["websocket"])


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
                from epistemic_platform.ontology.seed_loader import load_seed_actors
                await load_seed_actors(session)
                await session.commit()
            logger.info("Database initialized and seed actors loaded")
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

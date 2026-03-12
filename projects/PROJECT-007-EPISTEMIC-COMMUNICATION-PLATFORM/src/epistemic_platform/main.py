from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from epistemic_platform.config import get_settings

_PACKAGE_DIR = Path(__file__).resolve().parent


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
                "landing.html", {"request": request, "app_name": settings.app_name}
            )

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    _register_routers(app)
    _register_events(app)

    return app


def _register_routers(app: FastAPI) -> None:
    from epistemic_platform.routers import (
        actor_profile_router,
        user_profile_router,
        conversation_session_router,
        scenario_definition_router,
        auth_router,
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

        await engine.dispose()


app = create_app()

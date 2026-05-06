from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.settings import get_settings
from app.domains.identity.router import router as identity_router
from app.domains.organizations.router import router as organizations_router
from app.domains.tenancy.router import router as tenancy_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(identity_router)
    app.include_router(tenancy_router)
    app.include_router(organizations_router)
    return app


app = create_app()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.settings import get_settings
from app.domains.customers.router import router as customers_router
from app.domains.demo.router import router as demo_router
from app.domains.identity.router import router as identity_router
from app.domains.item_categories.router import router as item_categories_router
from app.domains.organizations.router import router as organizations_router
from app.domains.storage_locations.router import router as storage_locations_router
from app.domains.tenancy.router import router as tenancy_router
from app.domains.vendors.router import router as vendors_router


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

    app.include_router(demo_router)
    app.include_router(health_router, tags=["health"])
    app.include_router(identity_router)
    app.include_router(tenancy_router)
    app.include_router(customers_router)
    app.include_router(item_categories_router)
    app.include_router(organizations_router)
    app.include_router(storage_locations_router)
    app.include_router(vendors_router)
    return app


app = create_app()

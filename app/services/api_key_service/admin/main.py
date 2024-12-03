# admin/main.py
import os
from fastapi import FastAPI

from app.services.api_key_service.admin.routes.orchestration_routes import (
    OrchestrationRoutes,
)
from app.services.api_key_service.api_key_manager import ApiKeyManager
from fastapi import APIRouter

from app.services.api_key_service.database_service.pocketbase_service import (
    PocketBaseDatabaseService,
)


def create_admin_routes() -> APIRouter:
    router = APIRouter()

    pb_url = os.getenv("POCKETBASE_URL", "http://localhost:8090")
    pb_email = os.getenv("POCKETBASE_ADMIN_EMAIL")
    pb_password = os.getenv("POCKETBASE_ADMIN_PASSWORD")
    db_service = PocketBaseDatabaseService(pb_url, pb_email, pb_password)

    api_key_manager = ApiKeyManager(db_service)

    orchestration_routes = OrchestrationRoutes(api_key_manager)

    router.include_router(orchestration_routes.get_router())

    return router

from fastapi import FastAPI
from app.services.api_key_service.api_key_app import ApiKeyApp
from app.services.api_key_service.api_key_manager import ApiKeyManager
from app.services.api_key_service.database_service.pocketbase_service import (
    PocketBaseDatabaseService,
)
import os
from typing import Optional
import logging


class ApiKeyAppDriver:
    def __init__(
        self,
        pb_url: Optional[str] = None,
        pb_email: Optional[str] = None,
        pb_password: Optional[str] = None,
        jwt_key: Optional[str] = None,
    ):
        # Initialize PocketBase connection details
        self.pb_url = pb_url or os.getenv("POCKETBASE_URL", "http://localhost:8090")
        self.pb_email = pb_email or os.getenv("POCKETBASE_ADMIN_EMAIL")
        self.pb_password = pb_password or os.getenv("POCKETBASE_ADMIN_PASSWORD")

        # JWT encoder key for token generation
        self.jwt_key = jwt_key or os.getenv("JWT_ENCODER_KEY")

        if not all([self.pb_email, self.pb_password, self.jwt_key]):
            raise ValueError(
                "PocketBase admin credentials and JWT key must be provided"
            )

        # Set up the environment variable for JWT encoding
        os.environ["JWT_ENCODER_KEY"] = self.jwt_key

    def create_routes(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Log the database service initialization
        logger.info(f"Initializing PocketBaseDatabaseService with URL: {self.pb_url}, Email: {self.pb_email}")

        # Initialize database service
        db_service = PocketBaseDatabaseService(
            self.pb_url, self.pb_email, self.pb_password
        )

        # Create API key manager with database service
        api_key_manager = ApiKeyManager(db_service)

        # Initialize ApiKeyApp with the manager
        api_key_app = ApiKeyApp(api_key_manager)

        return api_key_app.get_router()


def create_api_key_routes(
    pb_url: Optional[str] = None,
    pb_email: Optional[str] = None,
    pb_password: Optional[str] = None,
    jwt_key: Optional[str] = None,
):
    driver = ApiKeyAppDriver(pb_url, pb_email, pb_password, jwt_key)
    return driver.create_routes()

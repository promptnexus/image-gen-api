# admin/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Annotated

from app.services.api_key_service.api_key_manager import ApiKeyManager
import logging

# Define the API key header schema
api_key_header = APIKeyHeader(name="X-API-Key")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdminKeyDependency:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.manager = api_key_manager

    async def verify_admin_api_key(
        self, api_key: Annotated[str, Depends(api_key_header)]
    ) -> str:
        """Verify if the provided API key is a valid admin key"""
        if not api_key:
            logger.warning("API key is missing")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is required"
            )

        if not self.manager.is_admin_api_key(api_key):
            logger.warning(f"Invalid API key: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

        logger.info(f"API key verified: {api_key}")
        return api_key

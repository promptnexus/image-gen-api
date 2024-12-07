# admin/services/orchestration.py
import logging
from typing import Any, NoReturn
from fastapi import HTTPException, status
from pydantic import EmailStr

from app.services.api_key_service.api_key_manager import ApiKeyManager
from app.services.api_key_service.models.apikey import ApiKey
from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User
from ..models.responses import (
    ErrorResponse,
    SuccessResponse,
    OrchestrationData,
    ApiKeyResponse,
)

logger = logging.getLogger(__name__)


class OrchestrationService:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.manager = api_key_manager
        self.db_service = api_key_manager.db_service

    async def create_user_organization_with_key(
        self,
        email: EmailStr,
        organization_name: str,
        api_key_name: str,
        customer_id: str,
    ) -> SuccessResponse:
        """
        Orchestrates the creation of a user, their organization, and an API key.
        Handles cleanup if any step fails.

        Args:
            email: User's email address
            organization_name: Name for the new organization
            api_key_name: Name for the API key to be generated

        Returns:
            SuccessResponse containing user, organization, and API key details

        Raises:
            HTTPException: If any step fails, with appropriate status code and cleanup
        """
        created_user = None
        created_org = None
        created_api_key = None

        try:
            # Step 1: Create user
            existing_user = self.db_service.get_user(email)
            if existing_user:
                logger.info(
                    f"User with email {email} already exists. Returning existing user."
                )
                created_user = existing_user
            else:
                logger.info(f"Creating user with email: {email}")
                created_user = self.db_service.create_user(email, "")

            logger.info(f"Successfully created user with ID: {created_user.id}")

            # Step 2: Create organization
            logger.info(
                f"Creating organization '{organization_name}' for user {created_user.id}"
            )

            created_org = self.manager.create_organization(
                organization_name, created_user.id
            )

            logger.info(f"Successfully created organization with ID: {created_org.id}")

            # Set customer ID if provided
            if customer_id is not None and len(customer_id) > 0:
                try:
                    logger.info(
                        f"Setting customer ID '{customer_id}' for organization {created_org.id}"
                    )
                    self.db_service.set_customer_id(created_org.id, customer_id)

                    logger.info(
                        f"Successfully set customer ID to [{customer_id}] for created organization {created_org.id}"
                    )
                except Exception as e:
                    logger.error(f"Failed to set customer ID: {str(e)}")
                    self._handle_cleanup_and_error(
                        e, created_user, created_org, created_api_key
                    )

            # Step 3: Generate API key
            logger.info(
                f"Generating API key '{api_key_name}' for organization {created_org.id}"
            )

            created_api_key = self.manager.generate_api_key(
                created_org.id,
                api_key_name,
            )

            logger.info(
                f"Successfully generated API key for organization {created_org.id}"
            )

            # If all steps succeeded, return the complete response
            return SuccessResponse(
                status="success",
                message="Successfully created user, organization, and API key",
                data=OrchestrationData(
                    api_key=ApiKeyResponse(
                        raw_key=created_api_key.raw_key,
                        name=created_api_key.name,
                        id=created_api_key.id,
                        organization_id=created_api_key.organization_id,
                    ),
                    organization_id=created_org.id,
                    user_id=created_user.id,
                    customer_id=customer_id,
                ),
            )

        except Exception as e:
            print("created user: ", created_user)
            self._handle_cleanup_and_error(
                e, created_user, created_org, created_api_key
            )

    def _handle_cleanup_and_error(
        self,
        original_error: Exception,
        created_user: User | None,
        created_org: Organization | None,
        created_api_key: ApiKey | None,
    ) -> NoReturn:
        """
        Handles cleanup of created resources and raises appropriate HTTP exception.
        The NoReturn type hint indicates this function always raises an exception.
        """
        error_message = f"Error during orchestration: {str(original_error)}"

        logger.error(error_message)

        try:
            # Clean up in reverse order
            print("Check to delete key")
            if created_api_key:
                logger.info(f"Cleaning up: Deleting API key {created_api_key}")
                self.manager.delete_api_key(created_api_key.id)

            print("Check to delete org")
            if created_org:
                logger.info(f"Cleaning up: Deleting organization {created_org.id}")
                self.manager.delete_organization(created_org.id, created_user.id)

            print("Check to delete user")
            if created_user:
                logger.info(f"Cleaning up: Deleting user {created_user.id}")
                self.db_service.delete_user(created_user.id)

        except Exception as cleanup_error:
            # If cleanup fails, log it but don't mask the original error
            logger.error(f"Error during cleanup: {str(cleanup_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    status="error",
                    message="Critical error: Operation failed and cleanup was unsuccessful",
                    error=str(original_error),
                    cleanup_error=str(cleanup_error),
                ).model_dump(),
            )

        # Raise the original error after successful cleanup
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                status="error",
                message="Operation failed but cleanup was successful",
                error=str(original_error),
            ).model_dump(),
        )

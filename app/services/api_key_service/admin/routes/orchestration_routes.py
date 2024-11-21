# admin/routes/orchestration_routes.py
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.api_key_service.admin.dependencies import AdminKeyDependency
from app.services.api_key_service.admin.models.requests import SetupOrganizationRequest
from app.services.api_key_service.admin.models.responses import SuccessResponse
from app.services.api_key_service.admin.services.orchestration_service import (
    OrchestrationService,
)


class OrchestrationRoutes:
    def __init__(self, api_key_manager):
        self.manager = api_key_manager
        self.router = APIRouter()
        self.admin_dependency = AdminKeyDependency(api_key_manager)
        self.orchestration_service = OrchestrationService(api_key_manager)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/setup-organization", response_model=SuccessResponse)
        async def setup_organization(
            request: SetupOrganizationRequest,
            authorization: str = Depends(self.admin_dependency.verify_admin_api_key),
        ):
            """
            Creates a new user, organization, and API key in one operation.
            Handles cleanup if any step fails.
            """

            email = request.email
            organization_name = request.organization_name
            api_key_name = request.api_key_name

            if not email or not organization_name or not api_key_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email, organization name, and API key name are required.",
                )

            try:
                result = (
                    await self.orchestration_service.create_user_organization_with_key(
                        email=email,
                        organization_name=organization_name,
                        api_key_name=api_key_name,
                    )
                )
                return result
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

    def get_router(self):
        return self.router

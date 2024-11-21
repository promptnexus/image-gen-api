# admin/models/responses.py
from pydantic import BaseModel
from typing import Literal

from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class ApiKeyResponse(BaseModel):
    raw_key: str
    name: str
    organization_id: str


class OrchestrationData(BaseModel):
    # user: User
    # organization: Organization
    api_key: ApiKeyResponse


class SuccessResponse(BaseModel):
    status: Literal["success"]
    message: str
    data: OrchestrationData


class ErrorResponse(BaseModel):
    status: Literal["error"]
    message: str
    error: str
    cleanup_error: str | None = None

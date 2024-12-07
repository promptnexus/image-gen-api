# admin/models/responses.py
from pydantic import BaseModel
from typing import Literal, Optional

from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class ApiKeyResponse(BaseModel):
    id: str
    raw_key: str
    name: str
    organization_id: str


class OrchestrationData(BaseModel):
    api_key: ApiKeyResponse
    organization_id: str
    user_id: str
    customer_id: Optional[str] = None


class SuccessResponse(BaseModel):
    status: Literal["success"]
    message: str
    data: OrchestrationData


class ErrorResponse(BaseModel):
    status: Literal["error"]
    message: str
    error: str
    cleanup_error: str | None = None

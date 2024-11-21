# admin/models/responses.py
from pydantic import BaseModel
from typing import Literal

from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class ApiKeyResponse(BaseModel):
    id: str
    raw_key: str
    name: str


class OrchestrationData(BaseModel):
    api_key: ApiKeyResponse
    organization_id: str
    user_id: str


class SuccessResponse(BaseModel):
    status: Literal["success"]
    message: str
    data: OrchestrationData


class ErrorResponse(BaseModel):
    status: Literal["error"]
    message: str
    error: str
    cleanup_error: str | None = None

# admin/models/requests.py
from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    email: str


class CreateOrganizationRequest(BaseModel):
    name: str
    user_id: str


class GenerateApiKeyRequest(BaseModel):
    name: str


class SetupOrganizationRequest(BaseModel):
    email: EmailStr
    organization_name: str
    api_key_name: str

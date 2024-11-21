from pydantic import BaseModel


class ApiKey(BaseModel):
    id: str
    hashed_key: str
    name: str
    organization_id: str


class AdminApiKey(BaseModel):
    id: str
    hashed_key: str
    name: str


class ApiKeyFull(ApiKey):
    raw_key: str

from pydantic import BaseModel


class ApiKey(BaseModel):
    hashed_key: str
    name: str
    organization_id: str

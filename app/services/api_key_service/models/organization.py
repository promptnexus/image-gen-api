from typing import List
from pydantic import BaseModel

from app.services.api_key_service.models.user import User


class Organization(BaseModel):
    id: str
    name: str
    admin_email: str
    members: List[User] = []

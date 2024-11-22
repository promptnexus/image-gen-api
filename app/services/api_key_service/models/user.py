from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    password: str
    is_admin: bool

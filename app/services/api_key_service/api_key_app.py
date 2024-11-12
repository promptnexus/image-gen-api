import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from pydantic import BaseModel
from jose import JWTError, jwt
from app.services.api_key_service.api_key_manager import ApiKeyManager


# New models for token handling
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    is_admin: bool


class Organization(BaseModel):
    id: str
    name: str
    admin_email: str


class ApiKeyApp:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.manager = api_key_manager
        self.router = APIRouter()
        self.templates = Jinja2Templates(directory="templates")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

        self.JWT_ENCODER_KEY = os.getenv("JWT_ENCODER_KEY")

        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self._setup_routes()

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.JWT_ENCODER_KEY, algorithm=self.ALGORITHM
        )
        return Token(access_token=encoded_jwt, token_type="bearer", expires_at=expire)

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, self.JWT_ENCODER_KEY, algorithms=[self.ALGORITHM]
            )

            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        user = self.manager.client.collection("users").get_first_list_item(
            f'email="{token_data.email}"'
        )
        if user is None:
            raise credentials_exception
        return user

    def _setup_routes(self):
        @self.manager.user_loader
        def load_user(email: str):
            user = self.manager.client.collection("users").get_first_list_item(
                f'email="{email}"'
            )
            if user:
                return User(email=user.email, is_admin=user.is_admin)
            return None

        @self.router.post("/auth/login")
        async def login_user(
            response: Response, form_data: OAuth2PasswordRequestForm = Depends()
        ):
            email = form_data.username
            password = form_data.password
            user = load_user(email)

            if not user or not self.manager.verify_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = self.create_access_token(data={"sub": email})

            response.set_cookie(
                key="access_token",
                value=f"Bearer {token.access_token}",
                httponly=True,
                secure=True,
                samesite="lax",
                expires=token.expires_at.timestamp(),
            )

            return token

        @self.router.post("/auth/logout")
        async def logout(response: Response):
            response.delete_cookie("access_token")
            return {"message": "Successfully logged out"}

        @self.router.get("/organizations", response_model=List[Organization])
        async def list_organizations(
            request: Request, current_user: User = Depends(self.get_current_user)
        ):
            org_records = self.manager.client.collection(
                "organizations"
            ).get_full_list()
            organizations = [
                Organization(id=org.id, name=org.name, admin_email=org.admin_email)
                for org in org_records
            ]
            return self.templates.TemplateResponse(
                "organizations.html",
                {"request": request, "organizations": organizations},
            )

        @self.router.post("/organizations", response_model=Organization)
        async def create_organization(
            request: Request,
            email: str,
            org_name: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org_record = self.manager.create_organization(org_name, email)
            return self.templates.TemplateResponse(
                "organization.html", {"request": request, "organization": org_record}
            )

        @self.router.post("/organizations/{org_id}/users")
        async def add_user_to_organization(
            org_id: str,
            user_email: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can add users to the organization",
                )
            self.manager.add_user_to_organization(org_id, user_email)
            return {"message": "User added successfully"}

        @self.router.delete("/organizations/{org_id}/users")
        async def delete_user_from_organization(
            org_id: str,
            user_email: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can delete users from the organization",
                )
            self.manager.delete_user_from_organization(org_id, user_email)
            return {"message": "User deleted successfully"}

        @self.router.get("/organizations/{org_id}/api-keys")
        async def get_api_keys(
            org_id: str, current_user: User = Depends(self.get_current_user)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or current_user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can view API keys",
                )
            api_keys = self.manager.get_api_keys(org_id)
            return api_keys

        @self.router.post("/organizations/{org_id}/api-keys")
        async def generate_api_key(
            org_id: str,
            key_name: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or current_user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can generate API keys",
                )
            api_key = self.manager.generate_api_key(org_id, key_name)
            return {"api_key": api_key}

        @self.router.get("/organizations/{org_id}/api-keys/{key_name}")
        async def fetch_api_key(
            org_id: str,
            key_name: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or current_user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can fetch API keys",
                )
            api_key = self.manager.fetch_api_key(org_id, key_name)
            return {"api_key": api_key}

        @self.router.delete("/organizations/{org_id}")
        async def delete_organization(
            org_id: str,
            admin_email: str,
            current_user: User = Depends(self.get_current_user),
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can delete the organization",
                )
            self.manager.delete_organization(org_id, admin_email)
            return {"message": "Organization deleted successfully"}

    def get_router(self):
        return self.router


def create_dashboard_route(api_key_manager: ApiKeyManager):
    api_key_app = ApiKeyApp(api_key_manager)
    return api_key_app.get_router()

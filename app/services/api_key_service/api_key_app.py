import os
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.api_key_service.api_key_manager import ApiKeyManager


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
        self.templates = Jinja2Templates(
            directory=os.path.join(os.path.dirname(__file__), "templates")
        )

        # Option 1: With prefix
        self.login_manager = LoginManager(
            secret=os.getenv("JWT_ENCODER_KEY"),
            token_url="/manage/auth/login",
            use_cookie=True,
        )

        # Option 2: Without prefix
        # self.login_manager = LoginManager(
        #     secret=os.getenv("JWT_ENCODER_KEY"),
        #     token_url="/auth/login",
        #     use_cookie=True,
        #     custom_exception=InvalidCredentialsException
        # )

        self.login_manager.user_loader(self.load_user)
        self._setup_routes()

    def load_user(self, email: str):
        user = self.manager.client.collection("users").get_first_list_item(
            f'email="{email}"'
        )
        if user:
            return User(email=user.email, is_admin=user.is_admin)
        return None

    def _setup_routes(self):
        @self.router.get("/auth/register", response_class=HTMLResponse)
        async def register_form(request: Request):
            return self.templates.TemplateResponse(
                "register.html", {"request": request}
            )

        @self.router.get("/auth/login", response_class=HTMLResponse)
        async def login_form(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.router.post("/auth/register")
        async def register(data: OAuth2PasswordRequestForm = Depends()):
            email = data.username
            password = data.password

            existing_user = self.load_user(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            self.manager.create_user(email, password)
            return RedirectResponse(url="/auth/login", status_code=302)

        @self.router.post("/auth/login")
        async def login(data: OAuth2PasswordRequestForm = Depends()):
            email = data.username
            password = data.password

            user = self.load_user(email)
            if not user:
                raise InvalidCredentialsException
            elif not self.manager.verify_password(password, user.password):
                raise InvalidCredentialsException

            token = self.login_manager.create_access_token(data={"sub": email})
            response = RedirectResponse(url="/manage/organizations", status_code=302)
            self.login_manager.set_cookie(response, token)
            return response

        @self.router.post("/auth/logout")
        def logout():
            response = RedirectResponse(url="/manage/auth/login", status_code=302)
            response.delete_cookie("access_token")
            return response

        @self.router.get("/organizations")
        async def list_organizations(
            request: Request, user=Depends(self.login_manager)
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

        @self.router.post("/organizations")
        async def create_organization(
            request: Request,
            email: str,
            org_name: str,
            user=Depends(self.login_manager),
        ):
            org_record = self.manager.create_organization(org_name, email)
            return self.templates.TemplateResponse(
                "organization.html", {"request": request, "organization": org_record}
            )

        @self.router.post("/organizations/{org_id}/users")
        async def add_user_to_organization(
            org_id: str, user_email: str, user=Depends(self.login_manager)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can add users to the organization",
                )
            self.manager.add_user_to_organization(org_id, user_email)
            return {"message": "User added successfully"}

        @self.router.delete("/organizations/{org_id}/users")
        async def delete_user_from_organization(
            org_id: str, user_email: str, user=Depends(self.login_manager)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can delete users from the organization",
                )
            self.manager.delete_user_from_organization(org_id, user_email)
            return {"message": "User deleted successfully"}

        @self.router.get("/organizations/{org_id}/api-keys")
        async def get_api_keys(org_id: str, user=Depends(self.login_manager)):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can view API keys",
                )
            api_keys = self.manager.get_api_keys(org_id)
            return api_keys

        @self.router.post("/organizations/{org_id}/api-keys")
        async def generate_api_key(
            org_id: str, key_name: str, user=Depends(self.login_manager)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can generate API keys",
                )
            api_key = self.manager.generate_api_key(org_id, key_name)
            return {"api_key": api_key}

        @self.router.get("/organizations/{org_id}/api-keys/{key_name}")
        async def fetch_api_key(
            org_id: str, key_name: str, user=Depends(self.login_manager)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or user.email not in org.members:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only members can fetch API keys",
                )
            api_key = self.manager.fetch_api_key(org_id, key_name)
            return {"api_key": api_key}

        @self.router.delete("/organizations/{org_id}")
        async def delete_organization(
            org_id: str, admin_email: str, user=Depends(self.login_manager)
        ):
            org = self.manager.client.collection("organizations").get_first_list_item(
                f'id="{org_id}"'
            )
            if not org or org.admin_email != user.email:
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

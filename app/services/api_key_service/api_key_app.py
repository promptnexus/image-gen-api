import os
from typing import Annotated, Optional, List
from fastapi import FastAPI, Depends, Form, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from jose import JWTError
from pydantic import BaseModel
import jwt

from app.services.api_key_service.api_key_manager import ApiKeyManager
from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

        @self.login_manager.user_loader()
        def load_user(email: str):
            print(f"Loading user: {email}")
            if not email:  # Handle cases where email is None or invalid
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": "/auth/login"},
                )
            return self.manager.db_service.get_user(email)

        # self.login_manager.user_loader(self.load_user)
        self._setup_routes()

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            # Need to provide the secret key and algorithm
            payload = jwt.decode(
                token,
                os.getenv("JWT_ENCODER_KEY"),
                algorithms=["HS256"],  # or whatever algorithm you're using for encoding
            )

            print("decoded token")
            print(payload)

            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=401, detail="Invalid authentication credentials"
                )
            user = self.load_user(username)  # Load user from your database
            if user is None:
                raise HTTPException(status_code=401, detail="User not found")
            return user
        except JWTError:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

    def load_user(self, email: str) -> User | None:
        """Load user for authentication"""
        return self.manager.db_service.get_user(email)

    def _setup_routes(self):
        @self.router.get("/auth/register", response_class=HTMLResponse)
        async def register_form(request: Request):
            return self.templates.TemplateResponse(
                "register.html", {"request": request}
            )

        @self.router.get("/auth/login", response_class=HTMLResponse)
        async def login_form(
            request: Request,
        ):
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.router.post("/auth/register")
        async def register(data: OAuth2PasswordRequestForm = Depends()):
            print(data)

            email = data.username
            password = data.password

            print(email)
            print(password)

            # Check if user already exists
            existing_user = self.manager.db_service.get_user(email)

            if existing_user:
                print("Already registered")

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            print("Registering user")

            # Create new user
            try:
                user = self.manager.db_service.create_user(email, password)

                # Generate token directly here instead of calling login
                token = self.login_manager.create_access_token(data={"sub": email})

                # Create response and set cookie
                response = RedirectResponse(
                    url="/manage/organizations", status_code=302
                )

                print(token)

                self.login_manager.set_cookie(response, token)

                return RedirectResponse(url="/manage/auth/login", status_code=302)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        @self.router.post("/auth/login")
        async def login(
            response: Response,
            data: OAuth2PasswordRequestForm = Depends(),
        ):
            email = data.username
            password = data.password

            print("logging in")
            print(email)
            print(password)

            # First use your service to authenticate the user
            user = self.manager.db_service.authenticate_user(email, password)

            print("got user")
            print(user)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # Create access token
            access_token = self.login_manager.create_access_token(
                data={"sub": email}  # 'sub' is required for the login manager to work
            )

            print("access token")
            print(access_token)

            # Set the cookie using login manager
            response = RedirectResponse(url="/manage/organizations", status_code=302)

            self.login_manager.set_cookie(response, access_token)

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
            print("list_organizations")
            print(user)
            try:
                print("user.email")
                print(user.email)

                organizations = self.manager.db_service.get_organizations(user.id)

                print("organizations")
                print(organizations)

                return self.templates.TemplateResponse(
                    "organizations.html",
                    {
                        "request": request,
                        "organizations": organizations,
                        "user_email": user.email,
                    },
                )
            except Exception as e:
                # Log the exception
                print(f"Error listing organizations: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while listing organizations",
                )

        @self.router.post("/organizations")
        async def create_organization(
            request: Request,
            name: str = Form(...),  # Explicitly indicate this is a form field
            user=Depends(self.login_manager),
        ):
            print("create_organization")
            print(name)

            org_record = self.manager.create_organization(name, user.id)

            print(org_record)

            # Redirect to the GET endpoint for organizations
            return RedirectResponse(url="/manage/organizations", status_code=303)

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

        @self.router.get("/organizations/{org_id}")
        async def get_api_keys(
            request: Request, org_id: str, user=Depends(self.login_manager)
        ):
            org = self.manager.get_organization(org_id, user.id)

            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found",
                )

            api_keys = self.manager.get_api_keys(org_id)
            return self.templates.TemplateResponse(
                "organizationpage.html",
                {
                    "request": request,
                    "api_keys": api_keys,
                    "organization_id": org_id,
                    "organization_name": org.name,
                    "user_email": user.email,
                },
            )

        @self.router.post("/organizations/{org_id}/api-keys")
        async def generate_api_key(
            org_id: str, key_name: str, user=Depends(self.login_manager)
        ):
            org = self.manager.get_organization(org_id, user.id)

            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found.",
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

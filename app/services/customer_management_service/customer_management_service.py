import os
from fastapi import APIRouter, HTTPException, Request, Depends, Header, status
from fastapi.responses import JSONResponse, RedirectResponse

from jose import jwt

import stripe
from typing import Optional

from app.services.api_key_service.admin.dependencies import AdminKeyDependency
from app.services.api_key_service.api_key_manager import ApiKeyManager
from app.services.api_key_service.database_service.pocketbase_service import (
    PocketBaseDatabaseService,
)

from fastapi_login import LoginManager
import json


class CustomerManagementService:
    def __init__(
        self,
        stripe_secret_key: str,
        webhook_secret: str,
        api_key_manager: ApiKeyManager,
    ):
        stripe.api_key = stripe_secret_key
        self.webhook_secret = webhook_secret
        self._init_database()

        self.manager = api_key_manager
        self.admin_dependency = AdminKeyDependency(api_key_manager)

        self.login_manager = LoginManager(
            secret=os.getenv("JWT_ENCODER_KEY"),
            token_url="/manage/auth/login",
            use_cookie=True,
        )

        @self.login_manager.user_loader()
        def load_user(email: str):
            print(f"Loading user: {email}")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": "/manage/auth/login"},
                )
            return self.db_service.get_user(email)

        self.router = self.create_customer_routes("manage")

    def form_user_dependency(self):
        def dependency(request: Request):
            session = request.cookies.get("access-token")
            if not session:
                raise HTTPException(status_code=401)

            payload = jwt.decode(
                session, os.getenv("JWT_ENCODER_KEY"), algorithms=["HS256"]
            )
            email = payload.get(
                "sub"
            )  # Since your token has the email in the 'sub' claim

            return self.db_service.get_user(email)

        return dependency

    def _init_database(self):
        """Initialize database connection"""
        pb_url = os.getenv("POCKETBASE_URL", "http://localhost:8090")
        pb_email = os.getenv("POCKETBASE_ADMIN_EMAIL")
        pb_password = os.getenv("POCKETBASE_ADMIN_PASSWORD")
        self.db_service = PocketBaseDatabaseService(pb_url, pb_email, pb_password)

    def get_customer_id(self, org_id: str) -> Optional[str]:
        """Get stripe customer ID for organization"""
        try:
            return self.db_service.get_customer_id(org_id)
        except Exception:
            return None

    def set_customer_id(self, org_id: str, customer_id: str):
        """Save stripe customer ID for organization"""
        try:
            self.db_service.set_customer_id(org_id, customer_id)
        except Exception as e:
            print(f"Error setting customer ID: {e}")
            raise HTTPException(status_code=500, detail="Failed to save customer ID")

    async def create_customer_session(
        self, org_id: str, user_email: str, success_url: str, cancel_url: str
    ) -> str:
        """Create either a setup or portal session based on customer status"""
        try:
            existing_customer = self.get_customer_id(org_id)

            if existing_customer:
                session = stripe.billing_portal.Session.create(
                    customer=existing_customer, return_url=success_url
                )
            else:
                session = stripe.checkout.Session.create(
                    mode="setup",
                    payment_method_types=["card"],
                    success_url=success_url,
                    cancel_url=cancel_url,
                    customer_email=user_email,
                    metadata={"organization_id": org_id},
                    customer_creation="always",
                )

            return session.url
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def set_customer_id_from_checkout(self, payload: bytes, signature: str):
        """Accepts a stripe webhook specifically after a checkout session. Used for our stripe checkout setup mode flow."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            org_id = session.get("metadata", {}).get("organization_id")

            customer_id = session.get("customer")

            # def print_json_tree(data, indent=0):
            #     for key, value in data.items():
            #         print(" " * indent + str(key) + ":")
            #         if isinstance(value, dict):
            #             print_json_tree(value, indent + 2)
            #         else:
            #             print(" " * (indent + 2) + str(value))

            # print_json_tree(event)

            if org_id and customer_id:
                print(f"Setting customer ID: {customer_id} for org: {org_id}")

                self.set_customer_id(org_id, customer_id)

        return {"status": "success"}

    def create_customer_routes(self, base_url: str):
        router = APIRouter()

        @router.post("/organizations/{org_id}/customer-session")
        async def create_stripe_session(
            request: Request, org_id: str, user=Depends(self.form_user_dependency())
        ):
            print(f"Creating session for org: {org_id}")

            # Verify user has access to this organization
            org = self.db_service.get_organization(org_id, user.id)

            if not org:
                raise HTTPException(status_code=404, detail="Organization not found")

            root_url = os.getenv("BASE_URL", "http://localhost:9000")

            success_url = f"{root_url}/{base_url}/organizations/{org_id}"
            cancel_url = success_url

            session_url = await self.create_customer_session(
                org_id=org_id,
                user_email=user.email,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return RedirectResponse(url=session_url, status_code=303)

        @router.post("/webhook")
        async def stripe_webhook(
            request: Request, stripe_signature: str = Header(None)
        ):
            payload = await request.body()
            return await self.set_customer_id_from_checkout(payload, stripe_signature)

        @router.post("/organizations/{org_id}/set-customer-id")
        async def set_customer_id(
            request: Request,
            org_id: str,
            customer_id: str,
            admin_api_key: str = Depends(self.admin_dependency),
        ):
            try:
                self.set_customer_id(org_id, customer_id)
                return JSONResponse(status_code=200, content={"status": "success"})
            except HTTPException as e:
                if e.status_code == 401:
                    return JSONResponse(
                        status_code=404, content={"detail": "Not found"}
                    )
                return JSONResponse(
                    status_code=e.status_code, content={"detail": str(e)}
                )
            except Exception as e:
                return JSONResponse(status_code=500, content={"detail": str(e)})

        return router

    def get_router(self):
        return self.router

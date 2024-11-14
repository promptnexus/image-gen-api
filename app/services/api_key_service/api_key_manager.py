import uuid
from app.services.api_key_service.database_service.database_service import (
    DatabaseService,
)
from pocketbase.models.record import Record
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_login import LoginManager
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


class ApiKeyManager:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def generate_api_key(self, org_id, key_name):
        api_key = str(uuid.uuid4())
        self.db_service.set_api_key(org_id, api_key, key_name)
        return api_key

    def fetch_api_key(self, org_id, key_name):
        return self.db_service.get_api_key(org_id, key_name)

    def create_organization(self, org_name, admin_email):
        return self.db_service.create_organization(org_name, admin_email)

    def add_user_to_organization(self, org_id, user_email):
        return self.db_service.add_user_to_organization(org_id, user_email)

    def get_organizations(self, org_id, user_email):
        return self.db_service.get_organizations(org_id, user_email)

    def get_api_keys(self, org_id):
        return self.db_service.get_api_keys(org_id)

    def delete_user_from_organization(self, org_id, user_email):
        return self.db_service.delete_user_from_organization(org_id, user_email)

    def delete_organization(self, org_id, admin_email):
        return self.db_service.delete_organization(org_id, admin_email)

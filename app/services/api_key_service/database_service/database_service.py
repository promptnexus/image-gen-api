from typing import Optional
from app.services.api_key_service.models.apikey import AdminApiKey, ApiKey
from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class DatabaseService:
    def get_organization_by_api_key(self, api_key):
        raise NotImplementedError

    def get_organization_customer_id_by_api_key(self, api_key):
        raise NotImplementedError

    def get_organization(self, org_id, user_id) -> Organization:
        raise NotImplementedError

    def set_api_key(self, org_id, api_key, key_name) -> ApiKey:
        raise NotImplementedError

    def get_api_key(self, org_id, key_name):
        raise NotImplementedError

    def get_api_keys(self, org_id):
        raise NotImplementedError

    def add_user_to_organization(self, org_id, user_email):
        raise NotImplementedError

    def delete_user_from_organization(self, org_id, user_email):
        raise NotImplementedError

    def create_organization(self, org_name, admin_id) -> Organization:
        raise NotImplementedError

    def get_organizations(self, user_id) -> list[Organization]:
        raise NotImplementedError

    def delete_organization(self, org_id, admin_email):
        raise NotImplementedError

    def create_user(self, email: str, password: str, is_admin: bool = False) -> User:
        raise NotImplementedError

    def get_user(self, email: str) -> User | None:
        raise NotImplementedError

    def authenticate_user(self, email: str, password: str) -> bool:
        raise NotImplementedError

    def find_api_key_data(self, api_key) -> ApiKey:
        raise NotImplementedError

    def find_admin_api_key_data(self, api_key) -> AdminApiKey:
        raise NotImplementedError

    def delete_user(self, id: str) -> None:
        raise NotImplementedError

    def delete_api_key(self, id):
        raise NotImplementedError

    def get_customer_id(self, org_id: str) -> Optional[str]:
        """Get stripe customer ID for organization"""
        raise NotImplementedError

    def set_customer_id(self, org_id: str, customer_id: str):
        """Save stripe customer ID for organization"""
        raise NotImplementedError

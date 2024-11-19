from app.services.api_key_service.models.user import User


class DatabaseService:
    def set_api_key(self, org_id, api_key, key_name):
        raise NotImplementedError

    def get_api_key(self, org_id, key_name):
        raise NotImplementedError

    def get_api_keys(self, org_id):
        raise NotImplementedError

    def add_user_to_organization(self, org_id, user_email):
        raise NotImplementedError

    def delete_user_from_organization(self, org_id, user_email):
        raise NotImplementedError

    def create_organization(self, org_name, admin_email):
        raise NotImplementedError

    def get_organizations(self, user_email):
        raise NotImplementedError

    def delete_organization(self, org_id, admin_email):
        raise NotImplementedError

    def create_user(self, email: str, password: str, is_admin: bool = False) -> User:
        raise NotImplementedError

    def get_user(self, email: str) -> User | None:
        raise NotImplementedError

    def authenticate_user(self, email: str, password: str) -> bool:
        raise NotImplementedError

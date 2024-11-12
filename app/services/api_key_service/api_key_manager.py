import uuid
from app.services.api_key_service.database_service.database_service import (
    DatabaseService,
)
from pocketbase.models.record import Record
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


class ApiKeyManager:
    def __init__(self, db_service: type[DatabaseService]):
        self.db_service = db_service()

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


# Example usage
# if __name__ == "__main__":
#     pb_url = "http://127.0.0.1:8090"
#     pb_email = "admin@example.com"
#     pb_password = "password"

#     db_service = PocketBaseDatabaseService(pb_url, pb_email, pb_password)
#     db_service.startup()

#     manager = ApiKeyManager(db_service)
#     org = manager.create_organization("My Organization", "admin@example.com")
#     print(f"Created Organization: {org}")

#     new_api_key = manager.generate_api_key(org.id)
#     print(f"Generated API Key: {new_api_key}")

#     fetched_api_key = manager.fetch_api_key(org.id)
#     print(f"Fetched API Key: {fetched_api_key}")

#     user = manager.add_user_to_organization(org.id, "user@example.com")
#     print(f"Added User to Organization: {user}")


# Example usage
# if __name__ == "__main__":
#   pb_url = 'http://127.0.0.1:8090'
#   pb_email = 'admin@example.com'
#   pb_password = 'password'

#   manager = ApiKeyManager(pb_url, pb_email, pb_password)
#   org = manager.create_organization('My Organization', 'admin@example.com')
#   print(f"Created Organization: {org}")

#   new_api_key = manager.generate_api_key(org.id)
#   print(f"Generated API Key: {new_api_key}")

#   fetched_api_key = manager.fetch_api_key(org.id)
#   print(f"Fetched API Key: {fetched_api_key}")

#   user = manager.add_user_to_organization(org.id, 'user@example.com')
#   print(f"Added User to Organization: {user}")
#   app = FastAPI()

#   SECRET = "your-secret-key"
#   manager = LoginManager(SECRET, token_url='/auth/token')

#   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# old

# class ApiKeyManager:
# def __init__(self, pb_url, pb_email, pb_password):
#     self.client = pocketbase.Client(pb_url)
#     self.client.admins.auth_with_password(pb_email, pb_password)
#     self.collection_name = "api_keys"

# def generate_api_key(self, org_id):
#     api_key = str(uuid.uuid4())
#     record = self.client.collection(self.collection_name).create(
#         {"organization_id": org_id, "api_key": api_key}
#     )
#     return api_key

# def fetch_api_key(self, org_id):
#     records = self.client.collection(self.collection_name).get_full_list(
#         query_params={"filter": f'organization_id="{org_id}"'}
#     )
#     if records:
#         return records[0].api_key
#     return None

# def create_organization(self, org_name, admin_email):
#     org_record = self.client.collection("organizations").create(
#         {"name": org_name, "admin_email": admin_email}
#     )
#     return org_record

# def add_user_to_organization(self, org_id, user_email):
#     user_record = self.client.collection("organization_users").create(
#         {"organization_id": org_id, "user_email": user_email}
#     )
#     return user_record


# class ApiKeyManager:
#     def __init__(self, db_service: DatabaseService):
#         self.db_service = db_service

#     def generate_api_key(self, org_id):
#         api_key = str(uuid.uuid4())
#         self.db_service.set_api_key(org_id, api_key)
#         return api_key

#     def fetch_api_key(self, org_id):
#         return self.db_service.get_api_key(org_id)

#     def create_organization(self, org_name, admin_email):
#         org_record = self.db_service.client.collection("organizations").create(
#             {"name": org_name, "admin_email": admin_email}
#         )
#         return org_record

#     def add_user_to_organization(self, org_id, user_email):
#         user_record = self.db_service.client.collection("organization_users").create(
#             {"organization_id": org_id, "user_email": user_email}
#         )
#         return user_record

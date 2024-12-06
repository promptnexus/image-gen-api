from typing import Optional
from app.services.api_key_service.database_service.database_service import (
    DatabaseService,
)
import pocketbase
import bcrypt

from app.services.api_key_service.helpers.api_key_generation import hash_api_key
from app.services.api_key_service.models.apikey import AdminApiKey, ApiKey
from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class PocketBaseDatabaseService(DatabaseService):
    def __init__(self, pb_url, pb_email, pb_password):
        self.client = pocketbase.Client(pb_url)
        self.client.admins.auth_with_password(pb_email, pb_password)

    # START: Billing Service access Customer ID from Organization
    def get_organization_by_api_key(self, api_key):
        api_key_data = self.find_api_key_data(api_key)

        if api_key_data:
            records = self.client.collection("organizations").get_full_list(
                query_params={"filter": f'id="{api_key_data.organization_id}"'}
            )
            if records:
                return records[0]

        return None

    def get_organization_customer_id_by_api_key(self, api_key):
        organization = self.get_organization_by_api_key(api_key)
        if organization:
            return organization.customer_id
        return None

    # END: Billing Service access Customer ID from Organization

    def get_organization(self, org_id, user_id) -> Organization:
        try:
            records = self.client.collection("organizations").get_full_list(
                query_params={
                    "filter": f'id="{org_id}" && (admin="{user_id}" || members ?~ "{user_id}")'
                }
            )

            if records:
                return records[0]
            return None
        except Exception as e:
            print(f"An error occurred while retrieving the organization: {e}")
            return None

    def find_api_key_data_generic(self, api_key, collection_name) -> ApiKey:
        hashed_key = hash_api_key(api_key)
        records = self.client.collection(collection_name).get_full_list(
            query_params={"filter": f'hashed_key="{hashed_key}"'}
        )
        if records:
            return records[0]
        return None

    def find_api_key_data(self, api_key) -> ApiKey:
        return self.find_api_key_data_generic(api_key, "api_keys")

    def find_admin_api_key_data(self, api_key) -> AdminApiKey:
        return self.find_api_key_data_generic(api_key, "admin_api_keys")

    def set_api_key(self, org_id, api_key, key_name) -> ApiKey:
        record = self.client.collection("api_keys").create(
            {"organization_id": org_id, "name": key_name, "hashed_key": api_key}
        )
        return record

    def get_api_key(self, org_id, key_name):
        records = self.client.collection("api_keys").get_full_list(
            query_params={
                "filter": f'organization_id="{org_id}" AND key_name="{key_name}"'
            }
        )
        if records:
            return records[0].api_key
        return None

    def get_api_keys(self, org_id):
        records = self.client.collection("api_keys").get_full_list(
            query_params={"filter": f'organization_id="{org_id}"'}
        )
        return [
            ({"name": record.name, "organization_id": record.organization_id})
            for record in records
        ]

    def create_organization(self, org_name, admin_id) -> Organization:
        org_record = self.client.collection("organizations").create(
            {"name": org_name, "admin": admin_id}
        )

        return Organization(
            id=org_record.id,
            name=org_record.name,
            admin=org_record.admin,
            members=org_record.members,
        )

    def get_organizations(self, user_id) -> list[Organization]:
        records = self.client.collection("organizations").get_full_list(
            query_params={"filter": f'members ?~ "{user_id}" || admin = "{user_id}"'}
        )

        if not records:
            return []

        org_ids = [record.id for record in records]
        organizations = []
        for org_id in org_ids:
            org_record = self.client.collection("organizations").get_one(org_id)
            organizations.append(org_record)

        return organizations

    def delete_organization(self, org_id, admin):
        org_record = self.client.collection("organizations").get_one(org_id)
        if org_record and org_record.admin == admin:
            self.client.collection("organizations").delete(org_id)
            return True
        return False

    def create_user(self, email: str, password: str, is_admin: bool = False) -> User:
        """
        Create a new user with hashed password
        """
        print("Creating user")

        user_data = {
            "email": email,
            "is_admin": is_admin,
        }

        if password:
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_data["password"] = hashed_password.decode("utf-8")

        # Print all user data entries
        all_users = self.client.collection("accounts").get_full_list()

        for user in all_users:
            print(user)

        try:
            record = self.client.collection("accounts").create(user_data)
            print(record)
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            return None

        return User(
            id=record.id,
            email=record.email,
            is_admin=record.is_admin,
            password=record.password,
        )

    def get_user(self, email: str) -> User | None:
        """
        Retrieve a user by email, including password for verification
        """
        try:
            record = self.client.collection("accounts").get_first_list_item(
                f'email = "{email}"'
            )

            return User(
                id=record.id,
                email=record.email,
                is_admin=record.is_admin,
                password=record.password,
            )
        except Exception:
            return None

    def authenticate_user(self, email: str, password: str) -> bool:
        """
        Authenticate a user by email and password
        """
        user = self.get_user(email)

        if not password:
            raise ValueError("Password cannot be empty")

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return True
        return False

    def delete_user(self, id: str) -> None:
        """
        Delete a user by their ID
        """
        try:
            self.client.collection("accounts").delete(id)
            print(f"User with ID {id} has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the user: {e}")

    def delete_api_key(self, id):
        try:
            self.client.collection("api_keys").delete(id)
            return True
        except Exception as e:
            print(f"An error occurred while deleting the API key: {e}")
            return False

    def get_customer_id(self, org_id: str) -> Optional[str]:
        org_data = self.client.collection("organizations").get_one(org_id)

        return org_data["customer_id"]

    def set_customer_id(self, org_id: str, customer_id: str):
        org_record = self.client.collection("organizations").get_one(org_id)

        if not org_record:
            msg = f"Organization with ID {org_id} not found."
            print(msg)
            raise Exception(msg)

        if org_record.get("customer_id"):
            msg = f"Customer ID already exists for organization {org_id}. Overwriting is not allowed. Verify manually."
            print(msg)
            raise Exception(msg)

        update_org = self.client.collection("organizations").update(
            org_id, {"customer_id": customer_id}
        )

        print(f"Succesfully set customer ID for organization {org_id}")

        return update_org

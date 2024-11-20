from app.services.api_key_service.database_service.database_service import (
    DatabaseService,
)
import pocketbase
import bcrypt

from app.services.api_key_service.models.organization import Organization
from app.services.api_key_service.models.user import User


class PocketBaseDatabaseService(DatabaseService):
    def __init__(self, pb_url, pb_email, pb_password):
        self.client = pocketbase.Client(pb_url)
        self.client.admins.auth_with_password(pb_email, pb_password)

    def get_organization(self, org_id, user_id):
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

    def get_api_key_by_hash(self, api_key_hash):
        records = self.client.collection("api_keys").get_full_list(
            query_params={"filter": f'hashed_key="{api_key_hash}"'}
        )
        if records:
            return records[0].api_key
        return None

    def set_api_key(self, org_id, key_name, api_key):
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

    def create_organization(self, org_name, admin_id):
        org_record = self.client.collection("organizations").create(
            {"name": org_name, "admin": admin_id}
        )
        return org_record

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

    def delete_organization(self, org_id, admin_email):
        org_record = self.client.collection("organizations").get_one(org_id)
        if org_record and org_record.admin_email == admin_email:
            self.client.collection("organizations").delete(org_id)
            return True
        return False

    def create_user(self, email: str, password: str, is_admin: bool = False) -> User:
        """
        Create a new user with hashed password
        """
        print("Creating user")
        # hashed_password = bcrypt.hash(password)
        # Correct usage:
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        print(hashed_password)

        user_data = {
            "email": email,
            "password": hashed_password.decode("utf-8"),
            "is_admin": is_admin,
        }

        print(user_data)

        # Print all user data entries
        all_users = self.client.collection("accounts").get_full_list()

        print(all_users)

        for user in all_users:
            print(user)

        try:
            record = self.client.collection("accounts").create(user_data)
            print(record)
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            return None

        return User(
            email=record.email, is_admin=record.is_admin, password=record.password
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

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return True
        return False

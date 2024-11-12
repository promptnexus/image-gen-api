from app.services.api_key_service.database_service.database_service import (
    DatabaseService,
)
import pocketbase


class PocketBaseDatabaseService(DatabaseService):
    def __init__(self, pb_url, pb_email, pb_password):
        self.client = pocketbase.Client(pb_url)
        self.client.admins.auth_with_password(pb_email, pb_password)

    def set_api_key(self, org_id, key_name, api_key):
        record = self.client.collection("api_keys").create(
            {"organization_id": org_id, "key_name": key_name, "api_key": api_key}
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
        return [record.api_key for record in records]

    def add_user_to_organization(self, org_id, user_email):
        user_record = self.client.collection("organization_users").create(
            {"organization_id": org_id, "user_email": user_email}
        )
        return user_record

    def delete_user_from_organization(self, org_id, user_email):
        records = self.client.collection("organization_users").get_full_list(
            query_params={
                "filter": f'organization_id="{org_id}" AND user_email="{user_email}"'
            }
        )
        if records:
            self.client.collection("organization_users").delete(records[0].id)
            return True
        return False

    def create_organization(self, org_name, admin_email):
        org_record = self.client.collection("organizations").create(
            {"name": org_name, "admin_email": admin_email}
        )
        return org_record

    def get_organizations(self, user_email):
        records = self.client.collection("organization_users").get_full_list(
            query_params={"filter": f'user_email="{user_email}"'}
        )
        org_ids = [record.organization_id for record in records]
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

import os
import traceback
from app.services.api_key_service.database_service.pocketbase_service import (
    PocketBaseDatabaseService,
)
from app.services.billing.models import ComputeUsage


class BillingService:
    def __init__(self):
        pb_url = os.getenv("POCKETBASE_URL", "http://localhost:8090")
        pb_email = os.getenv("POCKETBASE_ADMIN_EMAIL")
        pb_password = os.getenv("POCKETBASE_ADMIN_PASSWORD")
        self.db_service = PocketBaseDatabaseService(pb_url, pb_email, pb_password)

    def record_billing(self, duration: float, api_key: str):
        try:
            customer_id = self.db_service.get_organization_customer_id_by_api_key(
                api_key
            )

            self.record_compute_time(
                ComputeUsage(
                    customer_id=customer_id,
                    milliseconds=round(duration),
                )
            )
        except Exception as e:
            print(f"Error recording billing: {e}")
            traceback.print_exc()
            raise

    async def record_compute_time(self, usage: ComputeUsage):
        raise NotImplementedError

from decimal import Decimal

from app.services.billing.billing_provider import BillingProvider


class MockBilling(BillingProvider):
    async def charge_customer(
        self, customer_id: str, amount: Decimal, description: str
    ) -> str:
        mock_transaction_id = f"mock_tx_{hash(f'{customer_id}{amount}{description}')}"
        print(f"Mock billing - Charged customer {customer_id}: ${amount}")
        return mock_transaction_id

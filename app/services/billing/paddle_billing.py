from decimal import Decimal
from app.services.billing.billing_provider import BillingProvider
import paddle_billing as paddle


class PaddleBilling(BillingProvider):
    def __init__(self, api_key: str, sandbox: bool = True):
        self.client = paddle.Client(api_key=api_key, sandbox=sandbox)

    async def charge_customer(
        self, customer_id: str, amount: Decimal, description: str
    ) -> str:
        price = await self.client.prices.create(
            {
                "description": description,
                "unit_price": {"amount": str(amount), "currency_code": "USD"},
                "product_id": "your_product_id",
            }
        )

        transaction = await self.client.transactions.create(
            {
                "items": [{"price_id": price.id, "quantity": 1}],
                "customer_id": customer_id,
                "status": "ready",
                "collection_mode": "automatic",
            }
        )

        return transaction.id

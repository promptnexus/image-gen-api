from abc import ABC, abstractmethod
from decimal import Decimal


class BillingProvider(ABC):
    @abstractmethod
    async def charge_customer(
        self, customer_id: str, amount: Decimal, description: str
    ) -> str:
        """Charge customer and return transaction ID."""
        pass

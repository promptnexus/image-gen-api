from decimal import Decimal
from datetime import datetime
from .interfaces import BillingProvider
from .cost_calculator import CostCalculator, ComputeUsage
from .models import BillingRecord


class BillingService:
    def __init__(
        self,
        billing_provider: BillingProvider,
        cost_calculator: CostCalculator,
        markup_rate: Decimal = Decimal("1.01"),
    ):
        self.billing_provider = billing_provider
        self.cost_calculator = cost_calculator
        self.markup_rate = markup_rate

    async def process_charge(
        self,
        customer_id: str,
        compute_time: float,
        image_size: str,
        instance_type: str = "g4dn.xlarge",
    ) -> BillingRecord:
        # Calculate base cost
        usage = ComputeUsage(
            compute_time=compute_time,
            image_size=image_size,
            instance_type=instance_type,
        )
        base_cost = await self.cost_calculator.calculate_cost(usage)

        # Apply markup
        final_cost = (base_cost * self.markup_rate).quantize(Decimal("0.0001"))

        # Create charge
        transaction_id = await self.billing_provider.charge_customer(
            customer_id=customer_id,
            amount=final_cost,
            description=f"Image generation ({image_size}) on {instance_type} - {compute_time}s",
        )

        return BillingRecord(
            customer_id=customer_id,
            compute_time=compute_time,
            image_size=image_size,
            base_cost=base_cost,
            final_cost=final_cost,
            transaction_id=transaction_id,
        )

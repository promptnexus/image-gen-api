from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.services.billing.models import ComputeUsage


class CostCalculator(ABC):
    @abstractmethod
    async def calculate_cost_cents(self, usage: ComputeUsage) -> int:
        """Calculate raw compute cost in cents"""
        pass


class AWSCostCalculator(CostCalculator):
    # Costs in cents per hour (52.6 cents/hour becomes 5260)
    INSTANCE_HOURLY_RATES_CENTS: Dict[str, int] = {
        "g4dn.xlarge": 5260,  # $0.526/hour
        "g5.xlarge": 10060,  # $1.006/hour
    }

    # Costs in cents
    SIZE_COSTS_CENTS: Dict[str, int] = {
        "512x512": 10,  # $0.001
        "1024x1024": 20,  # $0.002
        "2048x2048": 40,  # $0.004
    }

    MS_PER_HOUR = 3_600_000  # 3600 seconds * 1000 ms

    async def calculate_cost_cents(self, usage: ComputeUsage) -> int:
        hourly_rate_cents = self.INSTANCE_HOURLY_RATES_CENTS[usage.instance_type]
        compute_cost_cents = (
            usage.compute_time_ms * hourly_rate_cents
        ) // self.MS_PER_HOUR
        size_cost_cents = self.SIZE_COSTS_CENTS.get(usage.image_size, 10)

        return compute_cost_cents + size_cost_cents


class MockCostCalculator(CostCalculator):
    async def calculate_cost_cents(self, usage: ComputeUsage) -> int:
        # $0.01 per second in cents
        mock_cost_cents = (usage.compute_time_ms * 100) // 1000  # Convert ms to cents
        print(
            f"Mock cost calculation: ${mock_cost_cents/100} for {usage.compute_time_ms/1000}s"
        )
        return mock_cost_cents


# Example helper function to convert to Paddle's expected format
def cents_to_paddle_amount(cents: int) -> str:
    """Convert cents to Paddle amount string"""
    return f"{cents/100:.2f}"

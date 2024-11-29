import os

import stripe

from app.services.billing.models import ComputeUsage
from app.services.billing.service import BillingService

stripe.api_key = os.getenv("STRIPE_API_KEY")


class StripeBillingService(BillingService):
    async def record_compute_time(self, usage: ComputeUsage):
        """Record compute time usage to Stripe's metered billing"""

        event_name = os.getenv("STRIPE_COMPUTE_USAGE_EVENT_NAME", "compute_time_usage")

        meter_event = stripe.billing.MeterEvent.create(
            event_name=event_name,
            payload={
                "value": str(usage.milliseconds),
                "stripe_customer_id": usage.customer_id,
            },
        )

        return meter_event

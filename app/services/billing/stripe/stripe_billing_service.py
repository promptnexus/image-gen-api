import os
import logging
import stripe

from app.services.billing.models import ComputeUsage
from app.services.billing.service import BillingService

stripe.api_key = os.getenv("STRIPE_API_KEY")

logger = logging.getLogger(__name__)


class StripeBillingService(BillingService):
    def __init__(self):
        super().__init__()

        self.api_key = os.getenv("STRIPE_API_KEY")

        if not self.api_key:
            logger.error("STRIPE_API_KEY environment variable is not set")
            raise ValueError("STRIPE_API_KEY is required")

        stripe.api_key = self.api_key

    async def record_compute_time(self, usage: ComputeUsage):
        """Record compute time usage to Stripe's metered billing"""

        print("Recording compute time usage to Stripe")

        try:
            event_name = os.getenv(
                "STRIPE_COMPUTE_USAGE_EVENT_NAME", "compute_time_usage"
            )

            if not usage.customer_id:
                logger.error("Missing customer_id in ComputeUsage")
                return None

            logger.info(
                f"Recording {usage.milliseconds}ms for customer {usage.customer_id}"
            )

            meter_event = await stripe.billing.MeterEvent.create_async(
                api_key=self.api_key,
                event_name=event_name,
                payload={
                    "value": usage.milliseconds,
                    "stripe_customer_id": usage.customer_id,
                },
            )

            logger.info(f"Successfully created Stripe meter event: {meter_event}")

        except stripe.error.StripeError as e:
            logger.error(f"Stripe API Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when recording compute time: {str(e)}")
            raise

        return meter_event

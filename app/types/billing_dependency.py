from app.services.billing.service import BillingService
from app.services.billing.stripe.stripe_billing_service import StripeBillingService


def get_billing_service() -> BillingService:
    return StripeBillingService()

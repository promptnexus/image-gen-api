from app.services.customer_management_service.customer_management_service import (
    CustomerManagementService,
)
import os

from app.services.api_key_service.api_key_manager import ApiKeyManager


def setup_customer_management(api_key_manager: ApiKeyManager):
    """Initialize customer management service and routes"""
    stripe_secret_key = os.getenv("STRIPE_API_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not stripe_secret_key or not webhook_secret:
        raise ValueError("Stripe secret key and webhook secret must be provided")

    cms = CustomerManagementService(
        stripe_secret_key=stripe_secret_key,
        webhook_secret=webhook_secret,
        api_key_manager=api_key_manager,
    )

    return cms


def get_new_customer_management_router():
    return setup_customer_management().get_router()

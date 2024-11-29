# # app/dependencies.py
# from typing import Optional
# from dataclasses import dataclass


# @dataclass
# class AppDependencies:
#     image_service: Optional["ImageGenerationService"] = None

#     @classmethod
#     def initialize(cls):
#         """Initialize all services"""
#         from app.services.image_generator import ImageGenerationService

#         return cls(image_service=ImageGenerationService())


# # app/resolvers/mutations/generic/generic.py
# import strawberry
# from typing import Optional
# from ....dependencies import AppDependencies


# app/dependencies.py
from app.services.billing.service import BillingService
from app.services.billing.stripe.stripe_billing_service import StripeBillingService
from app.services.image_generator import ImageGenerationService
import os


def get_image_generation_service() -> ImageGenerationService:
    return ImageGenerationService()


def get_billing_service() -> BillingService:
    return StripeBillingService()

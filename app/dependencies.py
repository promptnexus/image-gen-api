# app/dependencies.py
from typing import Optional
from dataclasses import dataclass


@dataclass
class AppDependencies:
    image_service: Optional["ImageGenerationService"] = None

    @classmethod
    def initialize(cls):
        """Initialize all services"""
        from app.services.image_generator import ImageGenerationService

        return cls(image_service=ImageGenerationService())


# app/resolvers/mutations/generic/generic.py
import strawberry
from typing import Optional
from ....dependencies import AppDependencies

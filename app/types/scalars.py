from typing import Any
import strawberry


@strawberry.scalar(
    name="PromptString",
    description="A string between 3 and 1000 characters for image generation prompts",
)
class PromptString:
    @staticmethod
    def serialize(value: str) -> str:
        return value

    @staticmethod
    def parse_value(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Prompt must be a string")
        if not (3 <= len(value) <= 1000):
            raise ValueError("Prompt must be between 3 and 1000 characters")
        return value


@strawberry.scalar(
    name="ImageCount",
    description="Number of images to generate (between 1 and 4)",
)
class ImageCount:
    @staticmethod
    def serialize(value: int) -> int:
        return value

    @staticmethod
    def parse_value(value: int) -> int:
        if not isinstance(value, int):
            raise ValueError("Image count must be an integer")
        if not (1 <= value <= 4):
            raise ValueError("Image count must be between 1 and 4")
        return value

from typing import Optional, List
import strawberry
from .enums import ImageFormat, ImageSize, ImageStyle


@strawberry.type
class ImageGenerationResult:
    id: str
    url: str
    created_at: str
    prompt: str
    format: ImageFormat
    size: ImageSize
    style: ImageStyle


@strawberry.type
class ImageGenerationError:
    message: str
    code: str


@strawberry.type
class ImageGenerationResponse:
    success: bool
    results: Optional[List[ImageGenerationResult]] = None
    error: Optional[ImageGenerationError] = None

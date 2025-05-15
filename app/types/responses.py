from typing import Optional, List
import strawberry
from .enums import ImageFormat, ImageStyle


@strawberry.type
class ImageGenerationResult:
    id: str
    image_base64: str
    created_at: str
    prompt: str
    image_format: ImageFormat
    width: int
    height: int
    style: ImageStyle
    url: Optional[str] = None


@strawberry.type
class ImageGenerationError:
    message: str
    code: str


@strawberry.type
class ImageGenerationResponse:
    success: bool
    results: Optional[List[ImageGenerationResult]] = None
    error: Optional[ImageGenerationError] = None

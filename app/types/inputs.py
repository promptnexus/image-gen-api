import strawberry

from app.types.enums import ImageFormat, ImageSize, ImageStyle
from app.types.scalars import PromptString, ImageCount


@strawberry.input
class ImageGenerationInput:
    prompt: PromptString
    format: ImageFormat = ImageFormat.PNG
    size: ImageSize = ImageSize.MEDIUM
    style: ImageStyle = ImageStyle.PHOTOREALISTIC
    num_images: ImageCount = strawberry.field(
        default=1, description="Number of images to generate"
    )

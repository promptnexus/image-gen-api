import strawberry
from .enums import ImageFormat, ImageSize, ImageStyle
from .scalars import PromptString, ImageCount


@strawberry.input
class ImageGenerationInput:
    prompt: PromptString
    format: ImageFormat = ImageFormat.PNG
    size: ImageSize = ImageSize.MEDIUM
    style: ImageStyle = ImageStyle.PHOTOREALISTIC
    num_images: ImageCount = strawberry.field(
        default=1, description="Number of images to generate"
    )

from typing import Optional
import strawberry

from app.types.enums import ImageFormat, ImageStyle, ModelType
from app.types.scalars import PromptString, ImageCount


@strawberry.input
class ImageGenerationInput:
    prompt: PromptString
    image_format: ImageFormat = ImageFormat.PNG
    width: Optional[int] = 512
    height: Optional[int] = 512
    style: ImageStyle = ImageStyle.PHOTOREALISTIC
    num_images: ImageCount = strawberry.field(
        default=1, description="Number of images to generate"
    )

    model_type: ModelType = strawberry.field(
        default=ModelType.STABLE_V2_1,
        description="Type of model to use for image generation",
    )

    num_inference_steps: Optional[int] = 50

from app.dependencies import get_image_generation_service
import strawberry
from strawberry.types import Info

from app.types.image_generation_input import ImageGenerationInput
from app.types.responses import (
    ImageGenerationResponse,
    ImageGenerationResult,
    ImageGenerationError,
)
from datetime import datetime
import uuid
import base64


@strawberry.type
class GenerateImageMutations:
    @strawberry.mutation(
        description="Generate one or more images based on the provided prompt and options"
    )
    async def generate_images(
        self,
        image_gen_input: ImageGenerationInput,
        info: Info,
    ) -> ImageGenerationResponse:
        """Generate images based on the input parameters."""
        try:
            image_service = get_image_generation_service()

            results = []
            for _ in range(image_gen_input.num_images):
                image_bytes = await image_service.generate(
                    image_gen_input=image_gen_input
                )

                image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                results.append(
                    ImageGenerationResult(
                        id=str(uuid.uuid4()),
                        image_base64=image_base64,
                        created_at=datetime.utcnow().isoformat(),
                        prompt=image_gen_input.prompt,
                        image_format=image_gen_input.image_format,
                        width=image_gen_input.width,
                        height=image_gen_input.height,
                        style=image_gen_input.style,
                    )
                )

            return ImageGenerationResponse(success=True, results=results)

        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error=ImageGenerationError(message=str(e), code="INTERNAL_ERROR"),
            )

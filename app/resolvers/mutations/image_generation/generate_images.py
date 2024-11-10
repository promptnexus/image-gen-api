from app.services.image_generator import ImageGenerationService
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


@strawberry.type
class GenerateImageMutations:
    def __init__(self):
        self.image_service = ImageGenerationService()

    @strawberry.mutation(
        description="Generate one or more images based on the provided prompt and options"
    )
    async def generate_images(
        self, input: ImageGenerationInput, info: Info
    ) -> ImageGenerationResponse:
        """Generate images based on the input parameters."""
        try:
            # Generate images
            results = []
            for _ in range(input.num_images):
                url = await self.image_service.generate(
                    model_type=input.model_type,
                    prompt=input.prompt,
                    width=input.width,
                    height=input.height,
                    num_inference_steps=input.num_inference_steps,
                )

                results.append(
                    ImageGenerationResult(
                        id=str(uuid.uuid4()),
                        url=url,
                        created_at=datetime.utcnow().isoformat(),
                        prompt=input.prompt,
                        format=input.format,
                        width=input.width,
                        height=input.height,
                        style=input.style,
                    )
                )

            return ImageGenerationResponse(success=True, results=results)

        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error=ImageGenerationError(message=str(e), code="INTERNAL_ERROR"),
            )

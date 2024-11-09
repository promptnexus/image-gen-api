from typing import Optional
import strawberry
from strawberry.types import Info
from ..types.inputs import ImageGenerationInput
from ..types.responses import (
    ImageGenerationResponse,
    ImageGenerationResult,
    ImageGenerationError,
)
from ..services.image import generate_image
from datetime import datetime
import uuid


@strawberry.type
class Mutation:
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
                url = await generate_image(
                    input.prompt, input.format, input.size, input.style
                )

                results.append(
                    ImageGenerationResult(
                        id=str(uuid.uuid4()),
                        url=url,
                        created_at=datetime.utcnow().isoformat(),
                        prompt=input.prompt,
                        format=input.format,
                        size=input.size,
                        style=input.style,
                    )
                )

            return ImageGenerationResponse(success=True, results=results)

        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error=ImageGenerationError(message=str(e), code="INTERNAL_ERROR"),
            )

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

# from rich.console import Console
# from rich.table import Table, box
# from rich.panel import Panel


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
            context = info.context

            print(f"Context: {context}")

            api_key = context["api_key"]

            print(f"API Key: {api_key}")

            image_service = get_image_generation_service()

            results = []
            print("\nImage Generation Settings:")
            print("------------------------")
            print(f"Prompt: {image_gen_input.prompt}")
            print(f"Format: {image_gen_input.image_format}")
            print(f"Width: {image_gen_input.width}")
            print(f"Height: {image_gen_input.height}")
            print(f"Style: {image_gen_input.style}")
            print(f"Number of Images: {image_gen_input.num_images}")
            print("------------------------\n")

            for _ in range(image_gen_input.num_images):

                print("we're in generate")

                try:
                    image_bytes = image_service.generate(
                        image_gen_input=image_gen_input,
                        api_key=api_key,
                    )

                except Exception as e:
                    print(f"Error generating image: {e}")
                    print(f"WHAT THE FUCk IS HAPPENING: {e}")
                    raise

                print("printing an image")
                print(f"Image bytes: {image_bytes}")

                image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                result = ImageGenerationResult(
                    id=str(uuid.uuid4()),
                    image_base64=image_base64,
                    created_at=datetime.utcnow().isoformat(),
                    prompt=image_gen_input.prompt,
                    image_format=image_gen_input.image_format,
                    width=image_gen_input.width,
                    height=image_gen_input.height,
                    style=image_gen_input.style,
                )

                results.append(result)

                print(f"Generated image result:")
                print(f"  ID: {result.id}")
                print(f"  Created at: {result.created_at}")
                print(f"  Prompt: {result.prompt}")
                print(f"  Format: {result.image_format}")
                print(f"  Dimensions: {result.width}x{result.height}")
                print(f"  Style: {result.style}")
                print("----------------------------------------")

            return ImageGenerationResponse(success=True, results=results)

        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error=ImageGenerationError(message=str(e), code="INTERNAL_ERROR"),
            )

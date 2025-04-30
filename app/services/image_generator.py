import os
import io

from app.services.timer import timer
from app.services.generator_service_config import build_gen_service_config
from app.services.model_loaders.load_model import load_model
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.services.utils import get_bytes, merge_inference_params
from app.types.billing_dependency import get_billing_service
from app.types.image_generation_input import ImageGenerationInput
import traceback


class ImageGenerationService:
    def __init__(self):
        cache_dir = os.getenv("MODEL_CACHE_DIR", "/tmp/model_cache")
        cache_dir = os.path.expanduser(cache_dir)  # Expands ~ to the home directory

        os.makedirs(cache_dir, exist_ok=True)

        hf_token = os.getenv("HF_TOKEN", None)

        self.config = build_gen_service_config(cache_dir=cache_dir, hf_token=hf_token)

        self.billing_service = get_billing_service()

    def generate(
        self,
        image_gen_input: ImageGenerationInput,
        api_key: str,
        **kwargs,
    ) -> bytes:
        """Generate an image and return raw bytes"""
        try:
            print("generate")
            print(f"API Key: {api_key}")

            print("Starting image generation process...")

            print("Registered pipelines:", PipelineRegistry._registry)

            model = load_model(image_gen_input.model_type, self.config)

            print(f"Model loaded: {image_gen_input.model_type}")

            pipeline_config = PipelineRegistry.get(image_gen_input.model_type)

            print(f"Pipeline config retrieved: {pipeline_config}")

            inference_params = merge_inference_params(
                pipeline_config_params=pipeline_config.inference_params,
                input_params=image_gen_input,
                kwargs=kwargs,
            )

            print(f"Final inference parameters: {inference_params}")

            image = None

            with timer(self.config.device) as inference_time:
                image = model(image_gen_input.prompt, **inference_params).images[0]

            print("Image generated successfully")

            # Convert PIL Image to bytes
            byte_stream = get_bytes(image_gen_input, image)

            print(
                f"Recording billing with inference_time={inference_time.value}, api_key={api_key}"
            )

            self.billing_service.record_billing(inference_time.value, api_key)

            print(f"Inference took {inference_time.value:.2f}ms")

            # print(byte_stream.getvalue())

            final_bytes = byte_stream.getvalue()

            print("returning final_bytes nextttttt")

            return final_bytes
        except Exception as e:
            print(f"Error generating image: {e}")
            traceback.print_exc()
            raise

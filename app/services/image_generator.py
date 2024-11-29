import os
from typing import Optional
from PIL import Image
import io
from pathlib import Path
from huggingface_hub import HfFolder

from app.dependencies import get_billing_service
from app.services import timer
from app.services.billing.models import ComputeUsage
from app.services.generator_service_config import build_gen_service_config
from app.services.model_loaders.load_model import load_model
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.services.utils import merge_inference_params
from app.types.enums import ModelType
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
        **kwargs,
    ) -> bytes:
        """Generate an image and return raw bytes"""
        try:
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
            byte_stream = io.BytesIO()
            image.save(byte_stream, format=image_gen_input.image_format.value)
            print("Image converted to bytes")

            self.billing_service.record_billing(inference_time, image_gen_input.org_id)

            print(f"Inference took {inference_time:.2f}ms")

            return byte_stream.getvalue()
        except Exception as e:
            print(f"Error generating image: {e}")
            traceback.print_exc()
            raise

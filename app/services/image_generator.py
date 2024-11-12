# app/services/image_generator.py
import os
from typing import Optional
from PIL import Image
import io
from pathlib import Path
from huggingface_hub import HfFolder

from app.services.generator_service_config import build_gen_service_config
from app.services.model_loaders.load_model import load_model
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.types.enums import ModelType
from app.types.image_generation_input import ImageGenerationInput


class ImageGenerationService:
    def __init__(self):
        cache_dir = os.getenv("MODEL_CACHE_DIR", "/tmp/model_cache")
        cache_dir = os.path.expanduser(cache_dir)  # Expands ~ to the home directory

        os.makedirs(cache_dir, exist_ok=True)

        hf_token = os.getenv("HF_TOKEN", None)

        self.config = build_gen_service_config(cache_dir=cache_dir, hf_token=hf_token)

        pass

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

            # Merge default inference params with any provided kwargs
            inference_params = {**pipeline_config.inference_params, **kwargs}
            print(f"Inference parameters: {inference_params}")

            # Overwrite inference params with input if available
            if image_gen_input.width:
                inference_params["width"] = image_gen_input.width
            if image_gen_input.height:
                inference_params["height"] = image_gen_input.height
            if image_gen_input.num_inference_steps:
                inference_params["num_inference_steps"] = (
                    image_gen_input.num_inference_steps
                )
            print(f"Final inference parameters: {inference_params}")

            image = model(image_gen_input.prompt, **inference_params).images[0]
            print("Image generated successfully")

            # Convert PIL Image to bytes
            byte_stream = io.BytesIO()
            image.save(byte_stream, format=image_gen_input.image_format.value)
            print("Image converted to bytes")
            return byte_stream.getvalue()
        except Exception as e:
            # Log the error
            print(f"Error generating image: {e}")
            raise

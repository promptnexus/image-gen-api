# app/services/image_generator.py
import os
from typing import Optional
from PIL import Image
import io
from pathlib import Path
from huggingface_hub import HfFolder

from app.services.generator_service_config import build_gen_service_config
from app.services.model_loaders import load_model
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.types.enums import ModelType
from app.types.image_generation_input import ImageGenerationInput


class ImageGenerationService:
    def __init__(self):

        cache_dir = os.getenv("MODEL_CACHE_DIR", "/tmp/model_cache")
        hf_token = os.getenv("HF_TOKEN", None)

        self.config = build_gen_service_config(cache_dir=cache_dir, hf_token=hf_token)

        pass

    def generate(
        self,
        input: ImageGenerationInput,
        model_type: ModelType,
        **kwargs,
    ) -> bytes:
        """Generate an image and return raw bytes"""
        model = load_model(model_type, self.config)
        pipeline_config = PipelineRegistry.get(model_type)

        # Merge default inference params with any provided kwargs
        inference_params = {**pipeline_config.inference_params, **kwargs}

        # Overwrite inference params with everything in input if available
        if input.width:
            inference_params["width"] = input.width
        if input.height:
            inference_params["height"] = input.height
        if input.num_inference_steps:
            inference_params["num_inference_steps"] = input.num_inference_steps

        image = model(input.prompt, **inference_params).images[0]

        # Convert PIL Image to bytes
        byte_stream = io.BytesIO()
        image.save(byte_stream, format="PNG")
        return byte_stream.getvalue()

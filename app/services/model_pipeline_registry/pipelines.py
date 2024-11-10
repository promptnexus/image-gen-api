from dataclasses import dataclass
from typing import Any, Dict, Type
from app.services.model_pipeline_registry.pipeline_registry import (
    PipelineConfig,
    PipelineRegistry,
)
from app.types.enums import ModelType
from diffusers import StableDiffusionPipeline, FluxPipeline


# Register Stable Diffusion pipeline
PipelineRegistry.register(
    ModelType.STABLE_V1_4,
    PipelineConfig(
        pipeline_class=StableDiffusionPipeline,
        default_params={"safety_checker": None},
        inference_params={"num_inference_steps": 50},
    ),
)

PipelineRegistry.register(
    ModelType.FLUX_1_DEV,
    PipelineConfig(
        pipeline_class=FluxPipeline,
        default_params={},
        inference_params={
            "height": 1024,
            "width": 1024,
            "guidance_scale": 3.5,
            "num_inference_steps": 50,
            "max_sequence_length": 512,
        },
        use_cpu_offload=True,  # FLUX default
    ),
)

# Register other Stable Diffusion pipelines
PipelineRegistry.register(
  ModelType.STABLE_V1_5,
  PipelineConfig(
    pipeline_class=StableDiffusionPipeline,
    default_params={"safety_checker": None},
    inference_params={"num_inference_steps": 50},
  ),
)

PipelineRegistry.register(
  ModelType.STABLE_V2_1,
  PipelineConfig(
    pipeline_class=StableDiffusionPipeline,
    default_params={"safety_checker": None},
    inference_params={"num_inference_steps": 50},
  ),
)

# Register other Flux pipelines
PipelineRegistry.register(
  ModelType.FLUX_2_DEV,
  PipelineConfig(
    pipeline_class=FluxPipeline,
    default_params={},
    inference_params={
      "height": 1024,
      "width": 1024,
      "guidance_scale": 3.5,
      "num_inference_steps": 50,
      "max_sequence_length": 512,
    },
    use_cpu_offload=True,
  ),
)

PipelineRegistry.register(
  ModelType.FLUX_3_DEV,
  PipelineConfig(
    pipeline_class=FluxPipeline,
    default_params={},
    inference_params={
      "height": 1024,
      "width": 1024,
      "guidance_scale": 3.5,
      "num_inference_steps": 50,
      "max_sequence_length": 512,
    },
    use_cpu_offload=True,
  ),
)
)

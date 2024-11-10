from typing import Dict
from app.services.model_pipeline_registry.types import PipelineConfig
from app.types.enums import ModelType
from diffusers import StableDiffusionPipeline, FluxPipeline


class PipelineRegistry:
    _registry: Dict[ModelType, PipelineConfig] = {}

    @classmethod
    def register(cls, model_type: ModelType, config: PipelineConfig):
        cls._registry[model_type] = config

    @classmethod
    def get(cls, model_type: ModelType) -> PipelineConfig:
        if model_type not in cls._registry:
            raise ValueError(f"No pipeline config registered for {model_type}")
        return cls._registry[model_type]

    @classmethod
    def register_pipelines(cls):
        # Register Stable Diffusion pipeline
        cls.register(
            ModelType.STABLE_V1_4,
            PipelineConfig(
                pipeline_class=StableDiffusionPipeline,
                default_params={"safety_checker": None},
                inference_params={"num_inference_steps": 50},
            ),
        )

        cls.register(
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
            ),
        )

        # Register other Stable Diffusion pipelines
        cls.register(
            ModelType.STABLE_V1_5,
            PipelineConfig(
                pipeline_class=StableDiffusionPipeline,
                default_params={"safety_checker": None},
                inference_params={"num_inference_steps": 50},
            ),
        )

        cls.register(
            ModelType.STABLE_V2_1,
            PipelineConfig(
                pipeline_class=StableDiffusionPipeline,
                default_params={"safety_checker": None},
                inference_params={"num_inference_steps": 50},
            ),
        )


# Register the pipelines
PipelineRegistry.register_pipelines()

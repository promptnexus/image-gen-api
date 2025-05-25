from typing import Dict
from app.services.model_pipeline_registry.custom_pipelines.mock_pipeline import (
    MockPipeline,
)
from app.services.model_pipeline_registry.types import PipelineConfig
from app.types.enums import ModelType
from diffusers import StableDiffusionPipeline, FluxPipeline
from diffusers.utils import pt_to_pil
from app.services.model_pipeline_registry.custom_pipelines.deep_floyd_pipeline import (
    DeepFloydCombinedPipeline,
)

from transformers import CLIPTokenizerFast


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

        cls.register(
            ModelType.FLUX_1_SCHNELL,
            PipelineConfig(
                pipeline_class=FluxPipeline,
                default_params={},
                inference_params={
                    "tokenizer": CLIPTokenizerFast,
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

        # stage_2 = DiffusionPipeline.from_pretrained(
        #     "DeepFloyd/IF-II-L-v1.0", text_encoder=None, variant="fp16", torch_dtype=torch.float16
        # )

        df_default_params = {
            "stage1": {
                "variant": "fp16",
            },
            "stage2": {
                "variant": "fp16",
                "text_encoder": None,
            },
            "stage3": {},
        }

        df_inference_params = {
            "noise_level": 100,
        }

        cls.register(
            ModelType.DEEPFLOYD_V1,
            PipelineConfig(
                pipeline_class=DeepFloydCombinedPipeline,
                default_params=df_default_params,
                inference_params=df_inference_params,
            ),
        )

        cls.register(
            ModelType.MOCK,
            PipelineConfig(
                pipeline_class=MockPipeline,
                default_params={"device": "mps"},
                inference_params={},
            ),
        )


# Register the pipelines
PipelineRegistry.register_pipelines()

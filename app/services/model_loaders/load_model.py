from typing import Any
from app.services.generator_service_config import GeneratorServiceConfig
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.types.enums import ModelType
import torch


def load_model(model_type: ModelType, config: GeneratorServiceConfig) -> Any:
    pipeline_config = PipelineRegistry.get(model_type)

    model = pipeline_config.pipeline_class.from_pretrained(
        model_type.value,
        torch_dtype=(
            torch.float16 if config.device in ["cuda", "mps"] else torch.float32
        ),
        cache_dir=config.cache_dir,
        use_auth_token=config.hf_token,
        **pipeline_config.default_params,
    )

    if pipeline_config.use_cpu_offload:
        model.enable_model_cpu_offload()
    else:
        model = model.to(config.device)

    return model

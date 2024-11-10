from typing import Any
from app.services.generator_service_config import GeneratorServiceConfig

from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry

from app.types.enums import ModelType
import torch


def load_model(model_type: ModelType, config: GeneratorServiceConfig) -> Any:
    print(f"Loading model for {model_type}")
    print(PipelineRegistry)
    print(PipelineRegistry._registry)

    try:
        pipeline_config = PipelineRegistry.get(model_type)
        print(pipeline_config)

    except ValueError:
        print(f"Pipeline config not found for {model_type}")

    print(f"Pipeline class for {model_type}: {pipeline_config.pipeline_class}")

    print(
        f"Has from_pretrained: {hasattr(pipeline_config.pipeline_class, 'from_pretrained')}"
    )

    model = pipeline_config.pipeline_class.from_pretrained(
        model_type.value,
        **pipeline_config.default_params,
        torch_dtype=(
            torch.float16 if config.device in ["cuda", "mps"] else torch.float32
        ),
        cache_dir=config.cache_dir,
        use_auth_token=config.hf_token,
    )

    if (
        hasattr(pipeline_config, "use_cpu_offload")
        and pipeline_config.use_cpu_offload
        and config.device == "cuda"
        and torch.cuda.is_available()
    ):
        model.enable_model_cpu_offload()
    else:
        model = model.to(config.device)

    return model

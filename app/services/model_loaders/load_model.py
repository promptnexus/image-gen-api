from typing import Any
from app.services.generator_service_config import GeneratorServiceConfig
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.types.enums import ModelType
import torch
import os


def load_model(model_type: ModelType, config: GeneratorServiceConfig) -> Any:
    print(f"Loading model for {model_type}")
    print(PipelineRegistry)
    print(PipelineRegistry._registry)

    # adjust the number of cores to you liking.
    num_cores = os.cpu_count() // 2
    torch.set_num_threads(num_cores)
    torch.set_num_interop_threads(num_cores // 2)
    os.environ["OMP_NUM_THREADS"] = str(num_cores)
    os.environ["MKL_NUM_THREADS"] = str(num_cores)

    try:
        pipeline_config = PipelineRegistry.get(model_type)
        print(pipeline_config)

    except ValueError:
        print(f"Pipeline config not found for {model_type}")

    print(f"Pipeline class for {model_type}: {pipeline_config.pipeline_class}")

    print(
        f"Has from_pretrained: {hasattr(pipeline_config.pipeline_class, 'from_pretrained')}"
    )

    if config.device in ["cuda", "mps"]:
        from torch.cuda.amp import autocast
        with autocast():
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float16,
                cache_dir=config.cache_dir,
                use_auth_token=config.hf_token,
            )
    else:
        model = pipeline_config.pipeline_class.from_pretrained(
            model_type.value,
            **pipeline_config.default_params,
            torch_dtype=torch.float32,
            cache_dir=config.cache_dir,
            use_auth_token=config.hf_token,
        )

    # model = pipeline_config.pipeline_class.from_pretrained(
    #     model_type.value,
    #     **pipeline_config.default_params,
    #     torch_dtype=(
    #         torch.float16 if config.device in ["cuda", "mps"] else torch.float32
    #     ),
    #     cache_dir=config.cache_dir,
    #     use_auth_token=config.hf_token,
    # )

    if (
            hasattr(pipeline_config, "use_cpu_offload")
            and pipeline_config.use_cpu_offload
            and config.device == "cuda"
            and torch.cuda.is_available()
    ):
        model.enable_model_cpu_offload()
    else:
        if config.device == "cpu":
            print("Setting CPU-specific optimizations...")
            torch.set_num_threads(num_cores)

    model = model.to(config.device)
    return model

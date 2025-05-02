from typing import Any
from app.services.generator_service_config import GeneratorServiceConfig
from app.services.model_pipeline_registry.pipeline_registry import PipelineRegistry
from app.types.enums import ModelType
import torch
import os
from rich.console import Console
from rich.table import Table


def display_pipeline_info(
    model_type: ModelType, config: GeneratorServiceConfig
) -> None:
    console = Console()

    # Create a table to display the pipeline information
    table = Table(title="Model Pipeline Information")

    table.add_column("Attribute", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add rows to the table
    table.add_row("Model Type", model_type.value)
    table.add_row("Configuration", str(config))

    # Print the table
    console.print(table)


def load_model(model_type: ModelType, config: GeneratorServiceConfig) -> Any:

    # Call the new function
    display_pipeline_info(model_type, config)

    try:
        pipeline_config = PipelineRegistry.get(model_type)
        print(pipeline_config)

    except ValueError:
        print(f"Pipeline config not found for {model_type}")
        return None

    print(f"Pipeline class for {model_type}: {pipeline_config.pipeline_class}")

    if config.device == "cuda":
        from torch.amp import autocast

        with autocast(device_type="cuda"):
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float16,
                cache_dir=config.cache_dir,
                use_auth_token=config.hf_token,
            )
    elif config.device == "mps":
        try:
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float16,
                cache_dir=config.cache_dir,
                use_auth_token=config.hf_token,
            )
        except RuntimeError as e:
            # Fallback to float32 if float16 fails on MPS
            print("Warning: float16 failed on MPS, falling back to float32")
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float32,
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
    # else:
    #     if config.device == "cpu":
    #         print("Setting CPU-specific optimizations...")
    #         torch.set_num_threads(num_cores)

    model = model.to(config.device)
    return model

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
    display_pipeline_info(model_type, config)

    try:
        pipeline_config = PipelineRegistry.get(model_type)
        print(pipeline_config)

    except ValueError:
        print(f"Pipeline config not found for {model_type}")
        return None

    print(f"Pipeline class for {model_type}: {pipeline_config.pipeline_class}")

    if config.device == "cuda":
        from rich.panel import Panel
        from rich.console import Console

        console = Console()

        float_type = "float16"
        device = config.device
        model_name = model_type.value

        # Prepare params for display
        params = dict(pipeline_config.default_params)
        params.update(
            {
                "model_name": model_name,
                "device": device,
                "float_type": float_type,
                "cache_dir": config.cache_dir,
                "token": config.hf_token,
                "local_files_only": True,
                "low_cpu_mem_usage": True,
                "torch_dtype": "torch.float16",
                "use_safetensors": True,
                "device_map": "balanced",
            }
        )

        # Format params for rich display
        param_lines = [
            f"[cyan]{k}[/cyan]: [magenta]{v}[/magenta]" for k, v in params.items()
        ]
        param_text = "\n".join(param_lines)

        console.print(
            Panel(
                f"[bold yellow]Loading Model[/bold yellow]: [green]{model_name}[/green]\n"
                f"[bold]Device:[/bold] [blue]{device}[/blue]    [bold]Float Type:[/bold] [red]{float_type}[/red]\n\n"
                f"[bold]Parameters:[/bold]\n{param_text}",
                title="🚀 Model Loading",
                border_style="bright_blue",
            )
        )

        model = pipeline_config.pipeline_class.from_pretrained(
            model_type.value,
            **pipeline_config.default_params,
            cache_dir=config.cache_dir,
            token=config.hf_token,
            local_files_only=True,  # don't download from HF
            low_cpu_mem_usage=True,  # streams layers instead of all at once
            torch_dtype=torch.float16,  # cast to float16
            use_safetensors=True,  # ~2× faster parse vs .p
            device_map="balanced",  # 🚀 stream shards straight onto GPU
            # offload_folder="offload",
            # offload_state_dict=True,
        )

        model.vae.enable_slicing()
        model.vae.enable_tiling()
        model.enable_attention_slicing()
        model.enable_sequential_cpu_offload()

    elif config.device == "mps":
        try:
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float16,
                cache_dir=config.cache_dir,
                token=config.hf_token,
            )
        except RuntimeError as e:
            # Fallback to float32 if float16 fails on MPS
            print("Warning: float16 failed on MPS, falling back to float32")
            model = pipeline_config.pipeline_class.from_pretrained(
                model_type.value,
                **pipeline_config.default_params,
                torch_dtype=torch.float32,
                cache_dir=config.cache_dir,
                token=config.hf_token,
            )
    else:
        model = pipeline_config.pipeline_class.from_pretrained(
            model_type.value,
            **pipeline_config.default_params,
            torch_dtype=torch.float32,
            cache_dir=config.cache_dir,
            token=config.hf_token,
        )

    if (
        hasattr(pipeline_config, "use_cpu_offload")
        and pipeline_config.use_cpu_offload
        and config.device == "cuda"
        and torch.cuda.is_available()
    ):
        model.enable_model_cpu_offload()

    model = model.to(config.device)
    return model

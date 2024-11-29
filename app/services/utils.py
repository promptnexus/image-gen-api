import torch

from app.types.image_generation_input import ImageGenerationInput


def pick_device() -> str:
    """Pick the best available device for PyTorch between CUDA, MPS, and CPU"""
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        print("WARNING: Running on CPU! Make sure CUDA/MPS is properly installed")
        return "cpu"


def merge_inference_params(
    pipeline_config_params: dict, input_params: ImageGenerationInput, kwargs: dict
) -> dict:
    """
    Merge and update inference parameters from multiple sources.

    Args:
        pipeline_config_params: Default inference parameters from pipeline config
        input_params: Image generation input parameters
        kwargs: Additional keyword arguments to override defaults

    Returns:
        dict: Final merged inference parameters
    """
    # Create a new dict by merging pipeline config with kwargs
    inference_params = {**pipeline_config_params, **kwargs}

    # Update with input parameters if they are provided (not None)
    if input_params.width is not None:
        inference_params["width"] = input_params.width
    if input_params.height is not None:
        inference_params["height"] = input_params.height
    if input_params.num_inference_steps is not None:
        inference_params["num_inference_steps"] = input_params.num_inference_steps

    return inference_params

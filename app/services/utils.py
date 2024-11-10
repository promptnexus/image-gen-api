import torch


def pick_device() -> str:
    """Pick the best available device for PyTorch between CUDA, MPS, and CPU"""
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        print("WARNING: Running on CPU! Make sure CUDA/MPS is properly installed")
        return "cpu"

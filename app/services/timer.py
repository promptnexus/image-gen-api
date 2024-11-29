import torch
import time
from contextlib import contextmanager
from torch.cuda import Event as CudaEvent
from torch.mps import Event as MpsEvent


@contextmanager
def timer(device=None):
    """Context manager for timing operations in milliseconds"""
    if device is None:
        from .utils import pick_device

        device = pick_device()

    if device == "cuda":
        start = CudaEvent(enable_timing=True)
        end = CudaEvent(enable_timing=True)
        start.record()
        yield
        end.record()
        torch.cuda.synchronize()
        return start.elapsed_time(end)
    elif device == "mps":
        start = MpsEvent(enable_timing=True)
        end = MpsEvent(enable_timing=True)
        start.record()
        yield
        end.record()
        torch.mps.synchronize()
        return start.elapsed_time(end)
    else:
        start = time.perf_counter()
        yield
        end = time.perf_counter()
        return (end - start) * 1000  # Convert to ms to match GPU timing

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

    class TimerResult:
        value: float = 0

    result = TimerResult()

    if device == "cuda":
        start = CudaEvent(enable_timing=True)
        end = CudaEvent(enable_timing=True)
        start.record()
        yield result
        end.record()
        torch.cuda.synchronize()
        result.value = start.elapsed_time(end)
    elif device == "mps":
        start = MpsEvent(enable_timing=True)
        end = MpsEvent(enable_timing=True)
        start.record()
        yield result
        end.record()
        torch.mps.synchronize()
        result.value = start.elapsed_time(end)
    else:
        start = time.perf_counter()
        yield result
        end = time.perf_counter()
        result.value = (end - start) * 1000  # Convert to ms to match GPU timing

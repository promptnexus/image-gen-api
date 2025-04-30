import time

import torch


from collections import namedtuple
from PIL import Image
import numpy as np

# Define the structure
Response = namedtuple("Response", ["images"])


class MockPipeline:
    """MockPipeline is a mock implementation of a model pipeline used for testing purposes.
    It simulates the loading and processing times to help test timers around the service.

    Methods:
      from_pretrained(cls, model_path=None, default_params=None, **kwargs):
        Class method to create an instance of MockPipeline with optional model path and default parameters.

      __init__(self, device="cuda", torch_dtype=torch.float16, default_params=None, **kwargs):
        Initializes the MockPipeline with the specified device, torch data type, and default parameters.
        Simulates a loading time of 10 seconds.

      enable_model_cpu_offload(self):
        Simulates enabling model CPU offload by printing a message.

      __call__(self, prompt, **inference_params):
        Simulates processing a prompt with a processing time of 10 seconds and returns a mock generated image.
    """

    @classmethod
    def from_pretrained(cls, model_path=None, default_params=None, **kwargs):
        """
        default_params = {
          "variant": "fp16"
        }
        """
        return cls(default_params=default_params or {}, **kwargs)

    def __init__(
        self, device="cuda", torch_dtype=torch.float16, default_params=None, **kwargs
    ):
        self.device = device
        self.dtype = torch_dtype
        default_params = default_params or {}

        print("Initializing pipeline...")
        time.sleep(1)  # Simulate loading time

    def enable_model_cpu_offload(self):
        print("Model CPU offload enabled")

    def __call__(self, prompt, **inference_params):
        print(f"Processing prompt: {prompt}")
        time.sleep(1)  # Simulate processing time

        # Create a small mock PIL image (10x10 black square)
        mock_image = Image.fromarray(np.zeros((10, 10, 3), dtype=np.uint8))

        return Response(images=[mock_image])

    def to(self, _):
        return self

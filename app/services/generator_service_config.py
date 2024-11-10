from pathlib import Path
from huggingface_hub import HfFolder
from app.services.utils import pick_device


class GeneratorServiceConfig:
    def __init__(
        self,
        cache_dir: Path,
        hf_token: str,
        device: str,
    ):
        self.cache_dir = cache_dir
        self.hf_token = hf_token
        self.device = device


def build_gen_service_config(
    cache_dir: str = "/tmp/model_cache", hf_token: str = None
) -> GeneratorServiceConfig:
    """Initialize the environment and return common configuration values"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True)

    if hf_token:
        HfFolder.save_token(hf_token)

    device = pick_device()

    return GeneratorServiceConfig(cache_dir, hf_token, device)

from dataclasses import dataclass
from typing import Any, Dict, Type


@dataclass
class PipelineConfig:
    pipeline_class: Type
    default_params: Dict[str, Any]
    inference_params: Dict[str, Any]
    use_cpu_offload: bool = False

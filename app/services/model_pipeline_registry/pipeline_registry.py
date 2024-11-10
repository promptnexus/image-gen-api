from dataclasses import dataclass
from typing import Any, Dict, Type
from app.types.enums import ModelType


@dataclass
class PipelineConfig:
    pipeline_class: Type
    default_params: Dict[str, Any]
    inference_params: Dict[str, Any]


class PipelineRegistry:
    _registry: Dict[ModelType, PipelineConfig] = {}

    @classmethod
    def register(cls, model_type: ModelType, config: PipelineConfig):
        cls._registry[model_type] = config

    @classmethod
    def get(cls, model_type: ModelType) -> PipelineConfig:
        if model_type not in cls._registry:
            raise ValueError(f"No pipeline config registered for {model_type}")
        return cls._registry[model_type]

from enum import Enum
import strawberry


@strawberry.enum
class ImageFormat(Enum):
    PNG = "PNG"
    JPEG = "JPEG"
    WEBP = "WEBP"


@strawberry.enum
class ImageStyle(Enum):
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"


@strawberry.enum
class ModelType(Enum):
    STABLE_V1_4 = "CompVis/stable-diffusion-v1-4"
    STABLE_V1_5 = "runwayml/stable-diffusion-v1-5"
    STABLE_V2_1 = "stabilityai/stable-diffusion-2-1"
    FLUX_1_DEV = "black-forest-labs/FLUX.1-dev"
    FLUX_1_SCHNELL = "black-forest-labs/FLUX.1-schnell"

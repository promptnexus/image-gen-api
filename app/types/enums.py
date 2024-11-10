from enum import Enum
import strawberry


@strawberry.enum
class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


@strawberry.enum
class ImageSize(Enum):
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"


@strawberry.enum
class ImageStyle(Enum):
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"

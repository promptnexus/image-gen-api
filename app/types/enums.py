import strawberry


@strawberry.enum
class ImageFormat:
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


@strawberry.enum
class ImageSize:
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"


@strawberry.enum
class ImageStyle:
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"

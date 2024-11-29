from app.services.image_generator import ImageGenerationService


def get_image_generation_service() -> ImageGenerationService:
    return ImageGenerationService()

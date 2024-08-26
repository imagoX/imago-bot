from runware import Runware, IImageInference
import logging
from misc import RUNWARE_API_KEY

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

models = {
    "AbsoluteReality": "civitai:81458@132760",
    "RealVisXL": "civitai:139562@344487",
    "ToonYou": "civitai:30240@102996",
    "SocaRealism": "civitai:158441@358398",
}

# List of banned words related to NSFW and violent content
BANNED_WORDS = [
    "nsfw", "nude", "violence", "gore", "blood", "sex", "kill", "murder", "death",
    "rape", "suicide", "porn", "drugs", "abuse", "assault", "rape", "weapon",
    "war", "torture", "crime",
]

async def generate_image(prompt: str, model: str) -> list[str]:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    request_image = IImageInference(
        positivePrompt=prompt,
        model=model,
        numberResults=4,
        negativePrompt="cloudy, rainy, nsfw, violent",
        useCache=False,
        height=1024,
        width=1024,
    )

    try:
        images = await runware.imageInference(requestImage=request_image)
        if images:
            return [image.imageURL for image in images]
        else:
            return []
    except Exception as e:
        logger.exception(f"Error during image generation: {e}")
        return []
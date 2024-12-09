from huggingface_hub import InferenceClient
from PIL import Image
import os

# Initialize Hugging Face client
client = InferenceClient(model="black-forest-labs/FLUX.1-dev", token="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")

def generate_image(prompt):
    """
    Generates an image based on the given prompt using the Hugging Face API.

    Args:
        prompt (str): The prompt for image generation.

    Returns:
        str: Path to the saved image.
    """
    try:
        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        # Generate image from Hugging Face API
        image = client.text_to_image(prompt)
        image_path = "static/generated_image.png"
        image.save(image_path)

        return image_path
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}")

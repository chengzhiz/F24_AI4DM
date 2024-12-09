from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv
import json
import random
from datetime import datetime

from langchain_openai import ChatOpenAI 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

from huggingface_hub import InferenceClient

import requests
from IPython.display import display

client = InferenceClient("black-forest-labs/FLUX.1-dev", token="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")

def generate_image(prompt):
    """
    Generates an image based on the given prompt using the Hugging Face API.

    Args:
        prompt (str): The prompt for the image generation.

    Returns:
        str: The path to the saved image.
    """
    try:
        if not prompt:
            raise ValueError("Prompt is required.")
        # Generate the image
        image = client.text_to_image(prompt)
        image_path = 'static/generated_image.png'
        image.save(image_path)
        return image_path
    except Exception as e:
        raise RuntimeError(f"Error generating image: {e}")
from huggingface_hub import InferenceClient
from PIL import Image
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

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
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    try:
        image = client.text_to_image(prompt)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs("static/generated_imgs", exist_ok=True)
        image_path = f"static/generated_imgs/image_{timestamp}.png"
        image.save(image_path)
        return image_path
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {str(e)}")


class ProjectUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'client' or 'designer'
    projects = db.relationship('ProjectUser', backref='user', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)


from huggingface_hub import InferenceClient
from PIL import Image
import os

from sqlalchemy import Text

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from sqlalchemy.dialects.postgresql import JSON  # Use for PostgreSQL

# Initialize Hugging Face client
client = InferenceClient(model="black-forest-labs/FLUX.1-dev", token="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")

def generate_image(prompt):
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

class Artboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    content = db.Column(Text)  # Use Text to store large text (JSON string)

    def __repr__(self):
        return f'<Artboard {self.id}>'

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from datetime import datetime
from model import generate_image  # Import your generate_image function

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/generated_imgs'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/artboard')
def artboard():
    return render_template('artboard.html', active='artboard')

@app.route('/about')
def about():
    return render_template('about.html', active='about')

@app.route('/generate_image', methods=['POST'])
def generate_image_endpoint():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        # Use the generate_image function from model.py
        image_path = generate_image(prompt)

        # Ensure the file is saved in the correct directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"image_{timestamp}.png"
        new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.rename(image_path, new_filepath)

        # Return the image URL
        image_url = f"/static/generated_imgs/{new_filename}"
        return jsonify({'image_url': image_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

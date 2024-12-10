from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from model import generate_image, db, Artboard, User, Project  # Import your generate_image function

from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate 

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/generated_imgs'

# Ensure proper setup of basedir
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'suqiuoiasjb'

# Initialize SQLAlchemy and Migrate
migrate = Migrate(app, db)  # Initialize migration with app and db

# Initialize the app with the db instance
db.init_app(app)


@app.route('/')
def home():
    some_project_id = 123  # Example value; replace with dynamic data as needed.
    return render_template("home.html", some_project_id=some_project_id)

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

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if User.query.filter_by(username=username).first():
        flash("Username already exists!")
        return redirect("/")

    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    flash("Account created successfully! Please log in.")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        flash("Invalid credentials. Please try again.")
        return redirect("/")

    session['user_id'] = user.id
    return redirect("/projects")

@app.route("/projects")
def projects():
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect("/login")  # Make sure you redirect to the login page

    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route("/join_project", methods=["POST"])
def join_project():
    try:
        if "user_id" not in session:
            flash("You need to log in first.")
            return redirect("/")

        project_id = request.form.get("project_id")
        password = request.form.get("password")

        if not project_id or not password:
            flash("Project ID and password are required.")
            return redirect("/projects")

        project = Project.query.filter_by(id=project_id).first()

        if project:
            if project.password == password:
                flash(f"Joined project: {project.name}")
                return redirect(url_for("artboard", project_id=project.id))
            else:
                flash("Invalid project password.")
        else:
            flash("Project not found.")

        return redirect("/projects")
    except Exception as e:
        print(f"Error in join_project: {e}")
        flash("An error occurred while joining the project.")
        return redirect("/projects")

@app.route("/artboard/<int:project_id>")
def artboard(project_id):
    try:
        # Query the database for the specific artboard based on the project ID
        artboard = Artboard.query.filter_by(project_id=project_id).first()

        if not artboard:
            return render_template("artboard.html", project_id=project_id, content=None)

        content = artboard.content
        print(f"Retrieved content for project {project_id}: {content}")  # Debugging

        if not content:
            flash("No content available for this artboard.")
            return render_template("artboard.html", project_id=project_id, content=None)

        try:
            # Try parsing the content as JSON
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            # If parsing fails, log the error and return the raw content
            print(f"Error decoding JSON content: {content}")
            flash("Error loading content: Invalid format.")
            return render_template("artboard.html", project_id=project_id, content=None)

        return render_template("artboard.html", project_id=project_id, content=parsed_content)

    except Exception as e:
        print(f"Error in artboard route: {e}")
        flash("An error occurred while loading the artboard.")
        return redirect("/projects")



@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect("/")

@app.route("/reset_projects", methods=["GET", "POST"])
def reset_projects():
    # Remove all existing projects
    Project.query.delete()
    db.session.commit()

    # Add new projects with real names
    new_projects = [
        Project(name="AI Research Hub", password="securepass1"),
        Project(name="Creative Design Studio", password="securepass2"),
        Project(name="Future Tech Lab", password="securepass3"),
    ]
    db.session.add_all(new_projects)
    db.session.commit()

    flash("Projects have been reset successfully.")
    return redirect("/projects")

@app.route("/save_artboard", methods=["POST"])
@app.route("/save_artboard/<int:project_id>", methods=["POST"])
def save_artboard(project_id=None):
    try:
        if request.is_json:
            content = request.json.get("content")
        else:
            content = request.form.get("content")

        print("Received content:", content)  # Debugging: Check the incoming content

        if not content:
            print("Error: No content provided.")
            return jsonify({"error": "Content is required"}), 400

        # If content is a dictionary or any other non-string type, convert it to JSON
        if isinstance(content, dict):
            content = json.dumps(content)

        # If project_id is provided in the URL, update the specific artboard
        if project_id:
            artboard = Artboard.query.filter_by(project_id=project_id).first()
            if not artboard:
                artboard = Artboard(project_id=project_id, content=content)
                db.session.add(artboard)
            else:
                print(f"Updating existing artboard with content: {content}")  # Debugging
                artboard.content = content
        else:
            artboard = Artboard(content=content)
            db.session.add(artboard)

        db.session.commit()

        print(f"Artboard saved with ID: {artboard.id}, content: {artboard.content}")  # Debugging

        if request.is_json:
            return jsonify({"message": "Artboard saved successfully", "artboard_id": artboard.id}), 200
        else:
            flash("Artboard saved successfully.")
            return redirect(url_for("artboard", project_id=project_id))

    except Exception as e:
        print(f"Error saving artboard: {e}")
        return jsonify({"error": "Failed to save artboard"}), 500


@app.route('/get_artboard/<projectId>', methods=['GET'])
def get_artboard(projectId):
    artboard_data = Artboard.query.filter_by(project_id=projectId).first()
    if artboard_data:
        return jsonify(success=True, data=artboard_data.content)
    else:
        return jsonify(success=False, error="Artboard not found")

    
if __name__ == "__main__":
    with app.app_context():
       print(db.metadata.tables.keys())
    app.run(debug=True)

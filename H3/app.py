from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
from model import generate_image, db, User, Project, ProjectUser  # Import your generate_image function

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
        return redirect("/")

    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route("/join_project", methods=["POST"])
def join_project():
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


@app.route("/artboard/<int:project_id>")
def artboard(project_id):
    artboard = Artboard.query.filter_by(project_id=project_id).first()
    return render_template("artboard.html", project_id=project_id, content=artboard.content if artboard else "")


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

class Artboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    content = db.Column(db.Text)  # Store artboard content as text

# In your app.py, when saving artboard data:
@app.route("/save_artboard/<int:project_id>", methods=["POST"])
def save_artboard(project_id):
    content = request.form.get("content")  # Assuming the data is from a form
    artboard = Artboard.query.filter_by(project_id=project_id).first()
    if not artboard:
        artboard = Artboard(project_id=project_id, content=content)
        db.session.add(artboard)
    else:
        artboard.content = content
    db.session.commit()
    flash("Artboard saved successfully.")
    return redirect(url_for("artboard", project_id=project_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)

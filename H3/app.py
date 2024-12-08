from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app =Flask(__name__, template_folder = 'templates', static_folder='static',static_url_path='/')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/artboard')
def artboard():
    return render_template('artboard.html', active='artboard')

@app.route('/about')
def about():
    return render_template('about.html', active='about')


if __name__ == '__main__':
    app.run(debug=True)
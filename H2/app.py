from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from model import ask_chatgpt, query, generate_question
from model2 import textGeneration_langChain_RAG, api_key
import os

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

@app.route('/')
def index():
    return render_template('about.html')

@app.route('/milestone1', methods=['GET', 'POST'])
def interaction1():
    # Load milestone1.html and pass an initial placeholder question
    question = "Waiting for a question..."
    answer = "waiting"  # Set a default empty answer
    category = "waiting"
    justification = "waiting"
    return render_template('milestone1.html', active='milestone1', question=question, 
                           answer=answer, category_name = category, justification = justification)

@app.route('/generate-question', methods=['GET'])
def generate_question_route():
    question = generate_question()  # This calls the function each time a request is made
    return jsonify({'question': question})

@app.route('/generate-question2', methods=['GET'])
def generate_question_route2():
    # Get the user type from the query parameters
    user_type = request.args.get('questionType')  # Use request.args to get the query parameter
    cwd = os.getcwd()
    retrieverDir = os.path.join(cwd, "chroma_db")

    # Call the new function with the necessary arguments
    question = textGeneration_langChain_RAG(user_type, retrieverDir, api_key)
    return jsonify({'question': question})

# New route to handle the ChatGPT question
@app.route('/ask-chatgpt', methods=['POST'])
def ask_chatgpt_route():
    data = request.get_json()
    user_input = data.get('question')  # Change this line to get 'question' instead of 'user_input'
    
    # Call the ask_chatgpt function and return its dictionary result directly
    response = ask_chatgpt(user_input)
    return jsonify(response)
  
@app.route('/milestone2', methods=['GET', 'POST'])
def interaction2():
    question = "Waiting for a question..."
    answer = "waiting"  # Set a default empty answer
    category = "waiting"
    justification = "waiting"
    
    return render_template('milestone2.html', active='milestone2', question=question, 
                           answer=answer, category_name = category, justification = justification)

@app.route('/takeaway')
def takeaway():
    return render_template('takeaway.html', active='takeaway')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

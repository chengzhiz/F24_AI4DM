from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv
import json
import random
from datetime import datetime

load_dotenv()

import requests

# https://huggingface.co/google/flan-t5-large?text=Please+give+me+a+simple+question+that+normal+people+ask+a+robot+that+can+be+answered+with+yes%2Fno.
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

# print("model.py",random_question)
# print("model.py",random_question[0]['generated_text'])

def generate_question():
    prompt_variations = [
        "Provide a simple fact-based yes/no question",
        "Provide a yes/no question that kids would ask",
        "Provide a yes/no question that adult would ask",
        "Provide a sophisticated yes/no question",
        "Provide a complicated yes/no question",
        "Provide an easy yes/no question",
    ]
    prompt = random.choice(prompt_variations)
    # prompt = f"Please give me a simple yes/no question. Random seed: {random.randint(1, 1000)} Time: {datetime.now()}"
    random_question = query({
		"inputs": prompt,
	})
    return random_question[0]['generated_text']

print("model.py Final Question:", generate_question())

def ask_chatgpt(user_input):
    """Send a question to ChatGPT and return the response."""
    client = OpenAI()
    # Construct the API call to GPT-4 with the appropriate messages, function calling, and response format
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a robot that answers each question with yes or no and the reason. Firstly, determine if the question is a yes/no question. If it's not, reply with 'None'. If it is a yes/no question, reply with yes/no, and then reply with exactly following sentences:\n\
                1. Personal and Contextual Insight: Chatbots don’t know your personal details and can’t provide advice specific to your life.\n\
                2. Emotions and Relationships: Chatbots don’t understand emotions or relationships, so they can’t offer advice on personal matters.\n\
                3. Personal Opinions and Preferences: Chatbots don’t have personal opinions, so they can’t advise on individual tastes.\n\
                4. Predicting the Future and Speculation: Chatbots can’t predict future events or answer speculative questions. They stick to known facts.\n\
                5. Medical and Legal Advice: Chatbots aren’t suitable for health or legal advice. Consult a professional in these fields.\n\
                6. Sensory and Perceptual Limitations: Chatbots work only with text and can’t interpret sounds, images, or physical sensations.\n\
                7. Artistic and Literary Interpretation: Chatbots lack personal insight, so they can’t interpret art or literature with emotional depth.\n\
                8. General Knowledge and Fact-Checking: Chatbots excel at general knowledge and fact-checking in areas like history, science, and technology.\n\
                9. Identity and Personhood: Chatbots are not human. They don’t have identities, genders, or personalities.\n\ "
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        functions=[
            {
                "name": "answer_categorize_question",
                "description": "Provides a yes/no answer, the category name, and a justification.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "enum": ["Yes", "no", "None"]
                        },
                        "category_name": {
                            "type": "string",
                            "description": "The full name of the category the question belongs to.",
                            "enum": [
                                "Personal and Contextual Insight",
                                "Emotions and Relationships",
                                "Personal Opinions and Preferences",
                                "Predicting the Future and Speculation",
                                "Medical and Legal Advice",
                                "Sensory and Perceptual Limitations",
                                "Questions Involving Human Emotions or Relationships",
                                "Interpretation of Art or Literature",
                                "General Knowledge and Fact-Checking",
                                "Identity and Personhood"
                            ]
                        },
                        "justification": {
                            "type": "string",
                            "description": "A one-sentence justification for why the question belongs to the category."
                        }
                    },
                    "required": ["answer", "category_name", "justification"]
                }
            }
        ],
        function_call="auto"  # Automatically call the function
    )

    # print(response)
    # Extract the function call from the response
    try:
        function_call = response.choices[0].message.function_call
        # print(function_call)
    except AttributeError:
        return {
            "answer": "None",
            "category_name": "None",
            "justification": "None"
        }
    # Parse the arguments of the function call

    try:
        arguments = function_call.arguments
        # print(arguments)
    except AttributeError:
        return {
            "answer": "None",
            "category_name": "None",
            "justification": "None"
        }

    parsed_data = json.loads(arguments)
    # Display the output: Answer, Category Name, and Justification
    answer = parsed_data["answer"]
    category_name = parsed_data["category_name"]
    justification = parsed_data["justification"]

    # Returning the structured response
    return {
        "answer": answer,
        "category_name": category_name,
        "justification": justification
    }

print("model.py Final Answer:", ask_chatgpt(generate_question()))

def runModels():
    results = ask_chatgpt(generate_question())
    return results




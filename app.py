from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
import re
import os
import string
import pickle
import google.generativeai as genai
from utils import randomString
from mongo import registerUser, checkUserIsExist, loginUser, postReview, fetchReviews, saveAns, getHistory as History
import hashlib

# Configure the Google AI API key
api_key = "AIzaSyBZsKYqXTzzvUyy9R23dtTAn5HQYVzGbEc"
genai.configure(api_key=api_key)

# Create the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 1048,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=generation_config,
)

# Function to generate predictions
def prediction(prompt):
    chat_session = model.start_chat(
        history=[]
    )
    response = chat_session.send_message(prompt)
    generated_text = response.text
    print(generated_text)
    return generated_text

def Predict(prompts):
    generated_answers = []
    for prompt in prompts:
        gen_text = prediction(prompt)
        print('gen => ', gen_text)
        generated_answers.append(gen_text.split())
    return generated_answers
# test()
app = Flask(__name__)
CORS(app)
ROOT = os.getcwd()
SEP = os.sep

@app.route('/images/<path:filename>')
def filesReq(filename):
    return send_from_directory('images', filename) 

@app.route('/login', methods=['POST'])
def Login():
    form = request.form
    user = form.get('user')
    password = form.get('password')
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    log = loginUser(user, password)
    if log:
        return log
    else:
        return {'message': 'email/username or password is incorrect! try again.', 'success': 0}


# @app.route('/get-news-res/<int:limit>/<int:skip>', methods=['GET'])
# def newsRes(limit=10, skip=0):
#     return getNewsRes(limit, skip)


@app.route('/sign-up', methods=['POST'])
def SignUp():
    form = request.form
    fullname = form.get('fullname')
    email = form.get('email')
    password = form.get('password')
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    file = request.files.get('avatar')
    checkExistency = checkUserIsExist(email)

    if checkExistency == 'email':
        return {'message': 'Email exist login with this email or add new.', 'success': 0}
    path = ''
    if file:
        file_name = randomString(14)
        ext = file.filename.split('.')[-1]
        path =  f"/images/{file_name}.{ext}"
        file.save(ROOT+path)
    user = registerUser({'fullname': fullname, 'email': email, 'password': password, 'avatar': path})
    return {'message': 'successfully registered!', 'success': 1, '_id': str(user.inserted_id), 'avatar': path}

@app.route('/get-history/', methods=['GET'])
def getHistory():
    return History()

@app.route('/get-reviews', methods=['GET'])
def getReviews():
    return fetchReviews()

@app.route('/post-review', methods=['POST'])
def addReview():
    form = request.form
    text = form.get('review')
    user_id = form.get('user_id')
    postReview(text, user_id)
    return {'message': 'successfully post.', 'success': 1} 


@app.route('/ask', methods=['POST'])
def AskQuestion():
    form = request.form
    question = form.get('text')
    user_id = form.get('user_id')
    ans = Predict([question])
    
    if question == '':
        return "EmptyRequest"
    saveAns(question, ans, user_id)
    return ans

@app.route('/')
def Home():
    return "Backend is working fine..."

if __name__ == '__main__':
    app.run(debug=True)
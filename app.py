from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz_db"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    if name:
        user_id = mongo.db.users.insert_one({'name': name}).inserted_id
        return redirect(url_for('select_module', user_id=user_id))
    return redirect(url_for('index'))

@app.route('/select_module/<user_id>')
def select_module(user_id):
    with open('data/modules.json') as f:
        modules = json.load(f)
    return render_template('select_module.html', user_id=user_id, modules=modules)

@app.route('/quiz/<user_id>/<module_id>')
def quiz(user_id, module_id):
    with open('data/questions.json') as f:
        questions = json.load(f)
    module_questions = [q for q in questions if q['module_id'] == module_id]
    return render_template('quiz.html', user_id=user_id, module_id=module_id, questions=module_questions)

@app.route('/submit_quiz/<user_id>/<module_id>', methods=['POST'])
def submit_quiz(user_id, module_id):
    score = 0
    with open('data/questions.json') as f:
        questions = json.load(f)

    module_questions = [q for q in questions if q['module_id'] == module_id]

    print("Form Data:", request.form)  # Debugging: See what user submitted

    for question in module_questions:
        q_id = str(question['_id'])  # Ensure consistent string format
        user_answer = request.form.get(q_id, "").strip().lower()  # Normalize input
        correct_answer = question['correct_answer'].strip().lower()  # Normalize correct answer

        print(f"QID: {q_id}, User Answer: {user_answer}, Correct Answer: {correct_answer}")  # Debugging

        if user_answer == correct_answer:
            score += 1

    print("Final Score:", score)  # Debugging

    # Save score to MongoDB
    mongo.db.scores.insert_one({'user_id': user_id, 'module_id': module_id, 'score': score})

    return redirect(url_for('result', user_id=user_id, module_id=module_id))

@app.route('/result/<user_id>/<module_id>')
def result(user_id, module_id):
    score_record = mongo.db.scores.find_one({'user_id': user_id, 'module_id': module_id})
    if score_record:
        return render_template('result.html', score=score_record['score'])
    else:
        return render_template('result.html', score="N/A")

@app.route('/score/<user_id>/<module_id>')
def score(user_id, module_id):
    score_record = mongo.db.scores.find_one({'user_id': user_id, 'module_id': module_id})
    if score_record:
        return render_template('score.html', score=score_record['score'])
    else:
        return render_template('score.html', score="N/A")


if __name__ == '__main__':
    app.run(debug=True)

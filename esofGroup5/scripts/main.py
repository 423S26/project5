from flask import Flask, jsonify, request
import csv

app = Flask(__name__)

questions = {}

def load_questions(filepath):
    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = {header: [] for header in headers}
        for row in reader:
            for i, value in enumerate(row):
                data[headers[i]].append(value)

    renamed = {}
    for key, values in data.items():
        question_text = values[0]
        renamed[question_text] = {
            "options": values[1:],
            "type": None
        }
    return renamed

@app.route('/upload', methods=['POST'])
def upload():
    global questions
    questions = load_questions("test.csv")
    return jsonify({"message": "CSV loaded", "questions": list(questions.keys())})

@app.route('/questions', methods=['GET'])
def get_questions():
    return jsonify(questions)

@app.route('/questions/set-type', methods=['POST'])
def set_type():
    data = request.json
    question = data.get("question")
    q_type = data.get("type")

    if question not in questions:
        return jsonify({"error": "Question not found"}), 404

    questions[question]["type"] = q_type
    return jsonify({"message": f"Type set for '{question}'", "question": questions[question]})

if __name__ == '__main__':
    app.run(debug=True)
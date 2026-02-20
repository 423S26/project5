from flask import Flask, jsonify, request
import csv
import io

app = Flask(__name__)

# In-memory store for parsed questions. Populated on /upload, read by /questions.
questions = {}

# Runs after every response — adds CORS headers so the browser allows
# requests from a different origin (e.g. an HTML file opened locally).
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Accepts a CSV file upload and parses it into questions.
# The Qualtrics export format has:
#   Row 1 - internal column IDs (e.g. "QID2") — used as dict keys during parsing
#   Row 2 - human-readable question text — becomes the final key
#   Rows 3+ - individual survey responses — stored as "options"
@app.route('/upload', methods=['OPTIONS', 'POST'])
def upload():
    # Browsers send a preflight OPTIONS request before a cross-origin POST.
    # We just acknowledge it so the actual POST is allowed through.
    if request.method == 'OPTIONS':
        return '', 204

    global questions

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Read the uploaded bytes and decode to a string so csv.reader can handle it.
    content = file.stream.read().decode('utf-8')
    reader = csv.reader(io.StringIO(content))

    # Row 1: internal Qualtrics column names — used as temporary keys.
    headers = next(reader)
    data = {header: [] for header in headers}

    # Collect every value in each column under its header key.
    for row in reader:
        for i, value in enumerate(row):
            if i < len(headers):
                data[headers[i]].append(value)

    # Rekey the dict: the first value in each column is the question text (row 2),
    # so use that as the key instead of the internal Qualtrics ID.
    renamed = {}
    for key, values in data.items():
        if not values:
            continue
        question_text = values[0]
        if question_text:
            renamed[question_text] = {
                "options": values[1:],  # rows 3+ are the actual responses
                "type": None            # type is unset until /questions/set-type is called
            }

    questions = renamed
    return jsonify({"message": "CSV loaded", "questions": list(questions.keys())})

# Returns the full questions dict as JSON.
# Useful for other pages (e.g. Analytics) to fetch questions without re-uploading.
@app.route('/questions', methods=['GET'])
def get_questions():
    return jsonify(questions)

# Lets a caller tag a question with a type (e.g. "likert", "multiple_choice").
# Expected JSON body: { "question": "<question text>", "type": "<type string>" }
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
    app.run(debug=True, port=5001)
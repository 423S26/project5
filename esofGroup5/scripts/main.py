from flask import Flask, render_template, url_for,jsonify, request, send_from_directory
import csv
import io
import os

app = Flask(__name__)

# Base directory is esofGroup5/ — one level up from this script.
# Used to locate and serve the frontend HTML and CSS files.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# In-memory store for parsed questions. Populated on /upload, read by /questions.
questions = {}


def auto_detect_type(question_text, responses):
    """
    Attempts to infer the question type from its text and response values.
    Returns one of: 'likert', 'ranking', 'multiple_choice', 'yes_no',
                    'rating', 'short_answer', or None if indeterminate.

    Strategy:
      1. Keyword matching on the question text (most reliable for Qualtrics exports).
      2. Response value analysis as a fallback.
    """
    text = question_text.lower()

    # --- Text-based detection ---
    likert_keywords = [
        'strongly disagree', 'strongly agree',
        'scale: 1-5', '1-strongly', '1 = strongly',
        'very dissatisfied', 'very satisfied',
        'level of agreement',
    ]
    ranking_keywords = [
        'rank', 'order of importance',
        'most important', 'least important',
        'drag and drop',
    ]
    multichoice_keywords = ['select all that apply']

    if any(k in text for k in likert_keywords):
        return 'likert'
    if any(k in text for k in ranking_keywords):
        return 'ranking'
    if any(k in text for k in multichoice_keywords):
        return 'multiple_choice'

    # --- Response value analysis ---
    non_empty = [r.strip() for r in responses if r.strip()]
    if not non_empty:
        return None

    unique_lower = set(v.lower() for v in non_empty)

    # Yes / No
    if unique_lower <= {'yes', 'no'}:
        return 'yes_no'

    # All numeric
    try:
        nums = [float(r) for r in non_empty]
        # Check if every value is a whole number
        if all(n == int(n) for n in nums):
            int_set = set(int(n) for n in nums)
            if int_set <= {1, 2, 3, 4, 5}:
                return 'likert'
            if int_set <= set(range(1, 8)):
                return 'ranking'
        return 'likert'
    except ValueError:
        pass

    # Small fixed set of repeated strings → multiple choice
    if len(unique_lower) <= 8 and len(non_empty) > len(unique_lower):
        return 'multiple_choice'

    # Default: free-text
    return 'short_answer'


# Serves the main page. On Render, the user hits the root URL and gets index.html.
@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/Analytics.html')
def Analytics():
    return send_from_directory(BASE_DIR, 'Analytics.html')

@app.route('/documentation.html')
def documentation():
    return send_from_directory(BASE_DIR, 'documentation.html')

@app.route('/Surveys.html')
def Surveys():
    return send_from_directory(BASE_DIR, 'Surveys.html')


# Serves the CSS file. The HTML references /style/style.css so Flask needs to handle it.
@app.route('/style/<path:filename>')
def styles(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'style'), filename)

# Serves JS files from the js directory.
@app.route('/js/<path:filename>')
def js_scripts(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'js'), filename)

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
            response_values = values[1:]
            renamed[question_text] = {
                "options": response_values,
                "type": auto_detect_type(question_text, response_values)
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
    # Render injects a PORT environment variable — use it if present, fall back to 5001 locally.
    # host='0.0.0.0' is required so Render can route external traffic to the server.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', debug=False, port=port)
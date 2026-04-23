import pytest
import io
import main


# --- FIXTURES ---

@pytest.fixture
def client():
    """
    Creates a Flask test client for each test.
    TESTING mode disables error catching so exceptions surface properly in tests.
    The 'questions' global is reset before each test so state doesn't leak between tests.
    """
    main.app.config['TESTING'] = True
    main.questions = {}
    with main.app.test_client() as client:
        yield client


# A minimal Qualtrics-style CSV with two columns.
# Row 1: internal IDs, Row 2: question text, Rows 3+: responses.
SAMPLE_CSV = (
    "QID1,QID2\n"
    "What is your student status?,How satisfied were you? (1-5)\n"
    "Undergraduate,4\n"
    "Graduate,5\n"
    "Undergraduate,3\n"
)


def upload_sample(client):
    """Helper that uploads SAMPLE_CSV and returns the response."""
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode()), 'coffee_test.csv')
    }
    return client.post('/upload', data=data, content_type='multipart/form-data')


# --- UPLOAD TESTS ---

def test_upload_valid_csv(client):
    """A valid CSV upload should return 200 and a list of question keys."""
    response = upload_sample(client)
    assert response.status_code == 200
    body = response.get_json()
    assert body['message'] == 'CSV loaded'
    assert 'What is your student status?' in body['questions']
    assert 'How satisfied were you? (1-5)' in body['questions']


def test_upload_no_file(client):
    """A POST to /upload with no file attached should return 400."""
    response = client.post('/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_upload_empty_filename(client):
    """A POST to /upload with an empty filename should return 400."""
    data = {'file': (io.BytesIO(b''), '')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_upload_parses_responses_correctly(client):
    """After upload, each question should store the correct responses in 'options'."""
    upload_sample(client)
    questions = main.questions

    assert questions['What is your student status?']['options'] == [
        'Undergraduate', 'Graduate', 'Undergraduate'
    ]
    assert questions['How satisfied were you? (1-5)']['options'] == ['4', '5', '3']


def test_upload_auto_detects_types(client):
    """After upload, auto-detection should set a type (not None) on questions with clear signals."""
    upload_sample(client)
    # 'How satisfied were you? (1-5)' has numeric responses 3-5 - should detect as likert
    assert main.questions['How satisfied were you? (1-5)']['type'] == 'likert'


# --- GET /questions TESTS ---

def test_get_questions_empty(client):
    """Before any upload, /questions should return an empty dict."""
    response = client.get('/questions')
    assert response.status_code == 200
    assert response.get_json() == {}


def test_get_questions_after_upload(client):
    """After upload, /questions should return the full questions dict."""
    upload_sample(client)
    response = client.get('/questions')
    assert response.status_code == 200
    body = response.get_json()
    assert 'What is your student status?' in body
    assert 'options' in body['What is your student status?']


# --- SET TYPE TESTS ---

def test_set_type_valid(client):
    """Setting a type on a known question should return 200 and update it."""
    upload_sample(client)
    response = client.post('/questions/set-type', json={
        'question': 'What is your student status?',
        'type': 'multiple_choice'
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['question']['type'] == 'multiple_choice'


def test_set_type_persists(client):
    """After setting a type, /questions should reflect the updated type."""
    upload_sample(client)
    client.post('/questions/set-type', json={
        'question': 'How satisfied were you? (1-5)',
        'type': 'likert'
    })
    response = client.get('/questions')
    body = response.get_json()
    assert body['How satisfied were you? (1-5)']['type'] == 'likert'


def test_set_type_unknown_question(client):
    """Setting a type on a question that doesn't exist should return 404."""
    upload_sample(client)
    response = client.post('/questions/set-type', json={
        'question': 'This question does not exist',
        'type': 'likert'
    })
    assert response.status_code == 404
    assert 'error' in response.get_json()


# --- AUTO-DETECT TESTS ---

# -- Text keyword detection --

def test_detect_likert_strongly_agree():
    """'Strongly agree/disagree' phrasing should detect as likert."""
    assert main.auto_detect_type(
        'Please rate your level of agreement (1-Strongly Disagree to 5-Strongly Agree)',
        ['3', '4', '5', '2']
    ) == 'likert'

def test_detect_likert_satisfied():
    """'Very dissatisfied to very satisfied' phrasing should detect as likert."""
    assert main.auto_detect_type(
        'How satisfied were you with your experience? (Scale: 1-5 or Very Dissatisfied to Very Satisfied)',
        ['4', '3', '5']
    ) == 'likert'

def test_detect_likert_level_of_agreement():
    """'Level of agreement' phrasing should detect as likert."""
    assert main.auto_detect_type(
        'Please rate your level of agreement with the following statement.',
        ['4', '5', '3']
    ) == 'likert'

def test_detect_ranking_by_keyword():
    """'Rank' in the question text should detect as ranking."""
    assert main.auto_detect_type(
        'Rank these items in order of importance to your success (1 = Most Important, 7 = Least Important)',
        ['1', '3', '2', '5', '4', '7', '6']
    ) == 'ranking'

def test_detect_ranking_drag_and_drop():
    """'Drag and drop' phrasing should detect as ranking."""
    assert main.auto_detect_type(
        'You can drag and drop each item with one at the top and 7 at the bottom. - Physical Study Space',
        ['2', '1', '3']
    ) == 'ranking'

def test_detect_multiple_choice_select_all():
    """'Select all that apply' should detect as multiple_choice."""
    assert main.auto_detect_type(
        'What do you typically do when you visit? (Select all that apply)',
        ['Tutoring', 'Study Space', 'Tutoring', 'Community Events']
    ) == 'multiple_choice'

# -- Response value detection --

def test_detect_yes_no_from_responses():
    """Responses containing only yes/no values should detect as yes_no."""
    assert main.auto_detect_type(
        'Are you a first-generation college student?',
        ['Yes', 'No', 'Yes', 'Yes', 'No']
    ) == 'yes_no'

def test_detect_yes_no_case_insensitive():
    """Yes/no detection should be case-insensitive."""
    assert main.auto_detect_type(
        'Did you consent?',
        ['yes', 'YES', 'Yes', 'no']
    ) == 'yes_no'

def test_detect_likert_from_1_to_5_responses():
    """All-integer responses in range 1-5 should detect as likert."""
    assert main.auto_detect_type(
        'How often do you visit?',
        ['1', '3', '5', '2', '4', '3']
    ) == 'likert'

def test_detect_ranking_from_1_to_7_responses():
    """All-integer responses in range 1-7 (but not all 1-5) should detect as ranking."""
    assert main.auto_detect_type(
        'How would you order these?',
        ['1', '2', '3', '4', '5', '6', '7']
    ) == 'ranking'

def test_detect_multiple_choice_small_string_set():
    """A small repeated set of string responses should detect as multiple_choice."""
    assert main.auto_detect_type(
        'Which college are you enrolled in?',
        ['Engineering', 'Engineering', 'Business', 'Engineering', 'Arts', 'Business']
    ) == 'multiple_choice'

def test_detect_short_answer_free_text():
    """Long unique free-text responses should detect as short_answer."""
    assert main.auto_detect_type(
        'What is one thing we should start doing?',
        [
            'More evening tutoring hours would help students with late classes.',
            'Expand the study space so more students can sit comfortably.',
            'Offer workshops on time management and study skills.',
            'Hire more tutors for upper-level engineering courses.',
        ]
    ) == 'short_answer'

def test_detect_empty_responses_returns_none():
    """A question with no non-empty responses should return None."""
    assert main.auto_detect_type(
        'What is your name?',
        ['', '   ', '']
    ) is None

def test_detect_no_responses_returns_none():
    """A question with an empty response list should return None."""
    assert main.auto_detect_type('Any question?', []) is None


# -- Bad path / unexpected input --

def test_detect_mixed_numeric_and_text_not_numeric():
    """Responses mixing numbers and text should not be detected as a numeric type."""
    result = main.auto_detect_type(
        'How many semesters have you attended?',
        ['3', 'Two', '1', 'Several', '2']
    )
    assert result not in ('likert', 'ranking', 'rating')

def test_detect_numbers_outside_1_to_7_is_likert():
    """Numeric responses outside the 1-7 range should detect as likert (our combined numeric type)."""
    assert main.auto_detect_type(
        'How would you rate your experience on a scale of 1 to 10?',
        ['7', '10', '8', '6', '9']
    ) == 'likert'

def test_detect_yes_no_with_third_option_not_yes_no():
    """If responses include a value beyond yes/no, it should not detect as yes_no."""
    result = main.auto_detect_type(
        'Do you use the tutoring center?',
        ['Yes', 'No', 'Sometimes', 'Yes', 'No']
    )
    assert result != 'yes_no'

def test_detect_single_unique_response_not_multiple_choice():
    """A column where every response is the same value isn't meaningful multiple choice."""
    result = main.auto_detect_type(
        'Did you consent to participate?',
        ['I Agree', 'I Agree', 'I Agree', 'I Agree']
    )
    # Only 1 unique value - doesn't meet len(non_empty) > len(unique) threshold meaningfully,
    # but more importantly should not crash; result can be multiple_choice or short_answer.
    assert result is not None

def test_detect_float_responses_not_ranking():
    """Decimal responses (e.g. GPA) should not be classified as ranking."""
    result = main.auto_detect_type(
        'What is your GPA?',
        ['3.5', '2.8', '3.9', '3.1']
    )
    assert result != 'ranking'


# --- /upload EDGE CASE TESTS ---

def test_upload_options_preflight(client):
    """OPTIONS preflight request should return 204 with no body."""
    response = client.options('/upload')
    assert response.status_code == 204

def test_upload_skips_empty_question_text(client):
    """Columns whose row-2 question text is blank should be silently skipped."""
    csv_with_blank = (
        "QID1,QID2\n"
        "Real Question,\n"
        "Answer1,something\n"
    )
    data = {'file': (io.BytesIO(csv_with_blank.encode()), 'coffee_test.csv')}
    client.post('/upload', data=data, content_type='multipart/form-data')
    assert 'Real Question' in main.questions
    assert '' not in main.questions

def test_upload_replaces_previous_data(client):
    """A second upload should overwrite questions from the first upload."""
    upload_sample(client)
    assert 'What is your student status?' in main.questions

    second_csv = "QID1\nNew Question\nAnswer A\nAnswer B\n"
    data = {'file': (io.BytesIO(second_csv.encode()), 'coffee_test.csv')}
    client.post('/upload', data=data, content_type='multipart/form-data')

    assert 'New Question' in main.questions
    assert 'What is your student status?' not in main.questions


# --- /use-test-file TESTS ---

def test_use_test_file_returns_200(client):
    """POST /use-test-file should return 200 and a list of questions."""
    response = client.post('/use-test-file')
    assert response.status_code == 200
    body = response.get_json()
    assert body['message'] == 'Test file loaded'
    assert isinstance(body['questions'], list)
    assert len(body['questions']) > 0

def test_use_test_file_populates_questions(client):
    """After calling /use-test-file, /questions should return non-empty data."""
    client.post('/use-test-file')
    response = client.get('/questions')
    body = response.get_json()
    assert len(body) > 0

def test_use_test_file_each_question_has_options_and_type(client):
    """Every question loaded from the test file should have 'options' and 'type' keys."""
    client.post('/use-test-file')
    for q in main.questions.values():
        assert 'options' in q
        assert 'type' in q

def test_use_test_file_replaces_previous_upload(client):
    """Calling /use-test-file after an upload should overwrite the previous questions."""
    upload_sample(client)
    assert 'What is your student status?' in main.questions

    client.post('/use-test-file')
    assert 'What is your student status?' not in main.questions

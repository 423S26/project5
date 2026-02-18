import csv


def load_questions(filepath):
    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)  # QID4, QID5, etc. - we'll skip these

        questions = {header: [] for header in headers}

        for row in reader:
            for i, value in enumerate(row):
                questions[headers[i]].append(value)

    # Rename keys to use the first value (actual question text) as the name
    renamed = {}
    for key, values in questions.items():
        question_text = values[0]  # e.g. "Are you 18 or older?"
        renamed[question_text] = values[1:]  # rest of the list = answer options

    return renamed


questions = load_questions("test.csv")

for question, options in questions.items():
    print(f"Question: {question}")
    print(f"Options: {options}")
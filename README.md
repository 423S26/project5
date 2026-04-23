# ESC Dashboard

**Analytics Dashboard for the Empower Student Center**

A web application that transforms Qualtrics survey CSV exports into interactive visualizations and statistics — reducing hours of manual Excel work to minutes.

Live app: [https://project5deploy.onrender.com](https://project5deploy.onrender.com)

> **Note:** The app is hosted on Render's free tier. If it hasn't been visited in a while, the first load may take 30-60 seconds to wake up.

---

## What It Does

1. **Upload** a Qualtrics CSV export (or use the built-in example file)
2. **Browse** all survey questions, search, and filter by type
3. **Select** a question to see a response preview and auto-detected question type
4. **Adjust** the question type if the auto-detection was wrong
5. **View** statistics and a generated chart (mean, median, mode, standard deviation where applicable)
6. **Download** the chart as a PNG

---

## Running Locally

### Requirements
- Python 3.9+
- A modern web browser (Chrome, Firefox, Safari, Edge)

### 1. Set up the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 2. Start the Flask backend

```bash
python backend/main.py
```

The server will start on **http://localhost:5001**.

> **macOS note:** Port 5000 is reserved by AirPlay Receiver, so we use 5001. If you see a 403 error, make sure you're hitting port 5001, not 5000.

### 3. Open the app

Navigate to **http://localhost:5001** in your browser. Do not open the HTML files directly — they need to be served through Flask for the upload endpoints to work.

### 4. Upload a CSV

On the **Upload** page, either:
- Click **Choose File** and select `backend/coffee_test.csv` (or any Qualtrics CSV export), then click **Upload File**
- Or click **Use Example File** to load the example coffee shop survey instantly

---

## Running Tests

```bash
pytest backend/test_main.py -v
```

36 tests covering upload parsing, question type auto-detection, and all API endpoints.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Backend | Python 3.9+, Flask |
| Deployment | Render (free tier) |
| Version Control | GitHub |
| CI | GitHub Actions (lint + tests on every push) |

---

## Project Structure

```
project5/
  frontend/         HTML, CSS, and JavaScript
  backend/          Flask app, tests, and example CSV
  .github/          CI workflows (lint + tests)
  index.html        GitHub Pages landing page
  README.md
  requirements.txt
  Makefile
```

---

## Makefile Commands

```bash
make run            # Start the Flask dev server
make test           # Run the test suite
make lint           # Run all linters (Python, HTML, JS)
make format         # Run all formatters
make check          # Format then lint
```

---

## Contact

### Project Team
- **Ari** - Backend Development, Data Science — osmunjai@gmail.com
- **Chrys** - Frontend Development, UX Design — howlhund@gmail.com

### Client
- **Susan** - Empower Student Center, Montana State University
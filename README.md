# ESC Dashboard

**Analytics Dashboard for the Empowerment Student Center**

*A proposed solution to transform Qualtrics survey data into actionable visualizations and statistics.*

---

## Running Locally

### Requirements
- Python 3.9+
- A modern web browser (Chrome, Firefox, Safari, Edge)

### 1. Set up the virtual environment

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install flask
```

### 2. Start the Flask backend

```bash
cd esofGroup5/scripts
python main.py
```

The server will start on **http://localhost:5001**.

> **macOS note:** Port 5000 is reserved by AirPlay Receiver, so we use 5001. If you see a 403 error, make sure you're hitting port 5001, not 5000.

### 3. Open the frontend

Open `esofGroup5/index.html` directly in your browser (File → Open, or drag it in).

### 4. Upload a CSV

Click **Choose File**, select `esofGroup5/scripts/test.csv` (or any Qualtrics CSV export), then click **Upload File**.

- A dropdown will appear with all survey questions.
- Select a question to see a preview of its responses.
- Use the **Question Type** selector to label the question, then click **Save Type**.

---

## Project Vision

### The Problem
The Empowerment Student Center (ESC) faculty member currently spends hours manually analyzing alumni exit survey data exported from Qualtrics.
This multi-step process involves:
1. Exporting CSV from Qualtrics
2. Manually analyzing data in Excel
3. Creating charts one-by-one
4. Calculating statistics manually
5. Formatting for presentations

This process is time-consuming and prevents staff from focusing on interpretation and strategic planning.

### Our Proposed Solution
The **ESC Dashboard** would be a web application that:
- Accepts CSV files exported from Qualtrics
- Helps user pick question types
- Generates appropriate visualizations
- Calculates relevant statistics
- Provides interactive filtering and customization

**Goal:** Reduce multi-hour analysis process to minutes.

### Why This Approach
- **User-Friendly** - Designed for administrators without technical backgrounds
- **Proposal-Ready** - Would help generate publication-quality outputs for funding proposals
- **All-in-One** - Single application combining parsing, visualization, and export

---

## Proposed Features

### Core Functionality (Planned)
- **Automatic CSV Upload** - One-click import of Qualtrics exports
- **Dynamic Visualizations** - Appropriate chart generation based on question type selected:
  - Multiple Choice → Pie charts or bar charts with percentages
  - Likert Scale → Stacked bar charts showing distribution
  - Numeric → Histograms or box plots with mean/median
  - Open-Ended Text → Word clouds showing common themes
- **Statistical Analysis** - Automatic calculation of means, medians, percentages, and other statistics depending on question type
- **Advanced Filtering** - Ability to filter by demographics, date ranges, and variables

### Potential Future Features (Stretch Goals)
- Custom chart styling and color schemes
- Save/load dashboard configurations
- An ability for Susan to save data

*Note: we are currently trying to have a small prototype for Susan so we can better understand what she needs*

---

## Planned Tech Stack

*These technologies have been selected for the project but not yet implemented.*

### Frontend (Proposed)
- **DJango** - Component-based UI framework
  - *Why:* Familiar to team, good for dashboard interfaces

### Backend (Proposed)
- **Python 3.11+** - Core language
  - *Why:* Strong data science ecosystem
- **Flask or FastAPI** - Web framework
  - *Decision pending:* Flask (simpler) vs FastAPI (better docs/performance)
- **Pandas** - Data manipulation
  - *Why:* Industry standard for data analysis
- **Matplotlib/Plotly** - Chart generation
  - *Decision pending:* Static (Matplotlib) vs Interactive (Plotly)

### Deployment (Proposed)
- **Vercel** - Frontend hosting (free tier)
- **Render** - Backend hosting (free tier)
- **GitHub** - Version control

---

## Intended Usage

*This describes how the application would work when implemented.*

### For End Users (Theoretical)

#### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- JavaScript enabled

#### Planned Access Method
1. Navigate to: `https://esc-dashboard.vercel.app` *(not yet deployed)*
2. No installation or login required
3. Bookmark for easy access

> **Note:** On free-tier hosting, first page load after 15+ minutes of inactivity may take 30-60 seconds for server to "wake up."

### Proposed User Workflow

**Step 1: Export from Qualtrics**
1. Log into Qualtrics
2. Open survey → Data & Analysis tab
3. Export & Import → Export Data
4. Select CSV format
5. Download file

**Step 2: Upload CSV (Theoretical)**
- Click "Upload CSV" or drag-and-drop file
- System processes (estimated 5-15 seconds)
- Preview data and parse questions

**Step 3: View Visualizations (Theoretical)**
- System automatically detects question types
- Generates appropriate charts
- Calculates statistics
- Displays interactive dashboard

**Step 4: Filter Data (Planned Feature)**
- Filter by demographics, dates, subgroups
- Visualizations update automatically

---

## Proposed System Architecture

*These diagrams represent our planned architecture, not implemented code.*

### Conceptual Component Diagram
```
┌─────────────────────────────────────────────────────────┐
│                User Interface (Planned)                 │
│                    (Django)                             │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Upload     │  Dashboard   │   Filter     │   Export   │
│  Component   │  Component   │  Component   │ Component  │
│  (Not built) │ (Not built)  │ (Not built)  │  (stretch) │
└──────┬───────┴──────┬───────┴──────┬───────┴─────┬──────┘
       │              │              │             │
       └──────────────┴──────────────┴─────────────┘
                      │
                      │
       ┌──────────────┴──────────────┐
       │                             │
┌──────▼─────────┐         ┌─────────▼────────┐
│   CSV parser   │         │  Visualization   │
│    Service     │         │     Service      │
│  (Proposed)    │         │   (Proposed)     │
└──────┬─────────┘         └─────────┬────────┘
       │                             │
       └──────────────┬──────────────┘
                      │
              ┌───────▼────────┐
              │  Data Analysis │
              │    Service     │
              │   (Proposed)   │
              └────────────────┘
```

### Theoretical Data Flow
```
User
 │
 │ 1. Would upload CSV
 ▼
Frontend (To be built)
 │
 │ 2. Would send CSV file via API
 ▼
Backend API (To be built)
 │
 │ 3. Would help parse & analyze
 ▼
CSV Parser → Question Selector (Both planned)
 │
 │ 4. Would generate visualizations
 ▼
Chart Generator (Planned)
 │
 │ 5. Would return data + charts
 ▼
Frontend Display (To be built)
 │
 │ 6. Would show dashboard
 ▼
User views results
```

### Hypothetical CSV Upload Flow
```
User          Frontend        Backend         Parser         Analyzer      Chart Gen
 │               │              │              │               │              │
 │ Upload CSV    │              │              │               │              │
 ├──────────────▶│              │              │               │              │
 │         (theoretical)        │              │               │              │
 │               │ POST /upload │              │               │              │
 │               ├─────────────▶│              │               │              │
 │               │        (to be implemented)  │               │              │
 │               │              │ Parse CSV    │               │              │
 │               │              ├─────────────▶│               │              │
 │               │              │        (planned logic)       │              │
 │               │              │              │ Question types│              │
 │               │              │              ├──────────────▶│              │
 │               │              │              │        (to be built)         │
 │               │              │              │               │ Generate     │
 │               │              │              │               │ charts       │
 │               │              │              │               ├─────────────▶│
 │               │              │              │               │  (planned)   │
 │               │              │◀─────────────┴───────────────┴──────────────┘
 │               │              │ Return JSON (would happen here)
 │               │◀─────────────┤
 │ Display       │              │
 │ Dashboard     │              │
 │◀──────────────┤              │

(All arrows represent planned functionality, not implemented code)
```

---

#### Hypothetical Setup Instructions

*These will work once code is implemented:*

**Frontend (Not yet available):**
```bash
cd frontend
npm install          # Dependencies don't exist yet
npm run dev          # No dev server to run yet
```

**Backend (Not yet available):**
```bash
cd backend
python -m venv venv           # Can create, but no code to run
source venv/bin/activate
pip install -r requirements.txt  # File doesn't exist yet
flask run --debug             # No Flask app to run yet
```

---

## Contact & Support

### Project Team
- **Ari** - Backend Development, Data Science
  - Email: osmunjai@gmail.com
- **Howl** - Frontend Development, UX Design
  - Email: howlhund@gmail.com

### Client
- **Susan** - Empowerment Student Center
- **Organization:** Montana State University

### Report Issues (When Application Exists)

**For End Users:**
- Email the team with:
  - Description of what you tried to do
  - What happened vs. what you expected
  - Error messages
  - Screenshots

**For Developers:**
- GitHub Issues (when repository is public)
- Bug report template (to be created)

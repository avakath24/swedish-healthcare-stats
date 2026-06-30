# 🇸🇪 Swedish Healthcare Statistics Dashboard

A SQL-based statistics dashboard exploring Swedish emergency department waiting times and ICD-10 diagnosis data — modeled on the kind of register-based statistics work done by **Socialstyrelsen** (Sweden's National Board of Health and Welfare), publishers of the National Patient Register.

**Live demo:https://swedish-healthcare-stats-denudrj8nahimjm8atuw66.streamlit.app/ 

---

## Why this project

Socialstyrelsen publishes ongoing statistics on emergency department waiting times, care-guarantee compliance, and disease/symptom statistics from the National Patient Register, and explicitly values SQL/SAS skills and ICD coding knowledge in their statistics roles. This project was built specifically to demonstrate that combination directly:

- Real, published Swedish healthcare statistics
- A genuine SQL database (SQLite) queried with raw SQL — not just pandas filtering
- ICD-10 diagnosis chapter classification, the same coding system used in the Patient Register

## What it does

- 📈 **National trend** — How have ER waiting times changed nationally from 2023-2025?
- 🌍 **Regional comparison** — Which regions have the longest/shortest ER stay times?
- 🏥 **Hospital-level extremes** — Which specific hospitals are fastest/slowest for time-to-doctor?
- 🩺 **ICD-10 chapters** — Reference table of diagnosis chapter codes, with a SQL **JOIN** example linking the "top admission cause by sex" data to its diagnosis chapter
- 📊 **Specialist care summary** — National-level 2024 figures on hospital admissions and patients

Every view includes an expandable "View SQL query used" section showing the actual SQL behind the chart — the dashboard doubles as a small showcase of SQL skills (`SELECT`, `WHERE`, `GROUP BY`, `ORDER BY ... LIMIT`, and a `JOIN`).

## Tech stack

- **SQLite** — a real, lightweight SQL database (a single `.db` file, no server needed) holding all the statistics tables
- **Raw SQL queries** (via Python's built-in `sqlite3` module) for all data retrieval — deliberately not just pandas filtering, to demonstrate SQL directly
- **pandas** to receive query results and pass them to the charts
- **Streamlit** for the interactive dashboard
- **Plotly** for charts

## Data provenance

All figures are real, published statistics from Socialstyrelsen's official reports and press releases:

- **National yearly ER statistics (2023-2025):** 2024 figures (≈1.8 million visits, median total stay 4h13m, median time-to-doctor reduced by 2 minutes from 2023) are directly from Socialstyrelsen's 2024 report and press release. 2025 figures (visits up 3%, median stay 4h15m, median time-to-doctor 61 minutes) are from Läkartidningen's coverage of the 2025 report. The 2023 and 2025 **visit counts** specifically are back-calculated from published year-over-year percentage changes rather than being independently published numbers — this is flagged with a `visits_estimated` column in the database for transparency.
- **Regional and hospital-level 2025 figures:** real published figures for the longest/shortest regions (stay time) and hospitals (time-to-doctor) from Läkartidningen's 2025 coverage.
- **Specialist care summary (2024):** real published national totals (4.443 million patients in specialist care, 1.377 million admissions, 824,000 hospitalized patients, cardiovascular disease as the top admission cause for men).
- **ICD-10 chapters:** the standard, publicly defined chapter structure of the ICD-10 classification (used internationally and adopted in Sweden as ICD-10-SE) — this is a classification standard, not original prose, so reproducing the chapter codes/names is standard practice in any health statistics system.

## Project structure

```
swedish-healthcare-stats/
├── app.py                   # Streamlit dashboard (main entry point)
├── analysis.py               # SQL query functions (the core SQL showcase)
├── healthcare_stats.db       # SQLite database (built by build_database.py)
├── requirements.txt
├── data/
│   └── build_database.py     # Builds the SQLite database from published figures
└── README.md
```

## Running it locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/swedish-healthcare-stats.git
cd swedish-healthcare-stats

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate       # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) rebuild the database from scratch
python3 data/build_database.py

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Possible extensions

- Add more years of data as new reports are published.
- Add more ICD-10 chapters and a fuller diagnosis-category breakdown.
- Swap SQLite for a connection to a real open Swedish statistics API, if/when one is reachable.
- Add a simple "write your own SQL query" text box in the Streamlit app for live querying.

---
*This is an educational/portfolio project and is not affiliated with or endorsed by Socialstyrelsen.*

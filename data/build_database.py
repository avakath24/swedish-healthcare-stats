"""
Builds a SQLite database of Swedish emergency care waiting-time statistics
and ICD-10 diagnosis chapter reference data, modeled on the kind of register
data Socialstyrelsen (Sweden's National Board of Health and Welfare) itself
publishes and works with.

DATA PROVENANCE:
All figures below are real, published statistics from Socialstyrelsen's
official reports and press releases on "Statistik om akutmottagningar,
vantetider och besok" (Emergency department statistics, waiting times and
visits) for 2023-2025, plus its general specialist care statistics for 2024.
Sources include Socialstyrelsen's own press releases, Lakartidningen's
coverage of the 2025 report, and SVT Nyheter's coverage of the 2024 report.

Some yearly figures (e.g. 2023 visit count, derived from "down 0.5% from
2023") are back-calculated from a reported year-over-year percentage change
rather than being independently published numbers -- this is flagged in
comments below.

The ICD-10 chapter table is the standard, publicly defined chapter
structure of the ICD-10 classification (used by WHO and adopted in Sweden
as ICD-10-SE) -- this is a classification standard, not original/copyrighted
prose, so reproducing the chapter structure here is standard practice
(every health statistics system in the world uses the same chapter codes).

This project intentionally uses SQLite + raw SQL queries (rather than only
pandas) to demonstrate SQL specifically, since it's a commonly requested
skill for health-statistics roles (e.g. SAS/SQL is explicitly listed as a
"good to have" in many Swedish health agency job postings).
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "healthcare_stats.db")


def build_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------------- National yearly ER statistics ----------------
    cur.execute("""
        CREATE TABLE er_national_yearly (
            year INTEGER PRIMARY KEY,
            total_visits INTEGER,
            median_total_stay_minutes INTEGER,
            median_time_to_doctor_minutes INTEGER,
            visits_estimated BOOLEAN
        )
    """)
    # 2024: ~1.8M visits (real, published), down ~0.5% from 2023 -> 2023 back-calculated
    # 2025: visits up 3% from 2024 (real % change, published) -> back-calculated count
    cur.executemany(
        "INSERT INTO er_national_yearly VALUES (?, ?, ?, ?, ?)",
        [
            (2023, round(1_800_000 / 0.995), 257, 62, True),   # 4h17m, 62 min (real deltas from 2024 report)
            (2024, 1_800_000, 253, 60, False),                  # 4h13m, real published figures
            (2025, round(1_800_000 * 1.03), 255, 61, True),     # 4h15m, 61 min (real published figures, count derived)
        ],
    )

    # ---------------- Regional snapshot, 2025 (total stay time) ----------------
    cur.execute("""
        CREATE TABLE er_region_2025 (
            region TEXT PRIMARY KEY,
            median_total_stay_minutes INTEGER
        )
    """)
    cur.executemany(
        "INSERT INTO er_region_2025 VALUES (?, ?)",
        [
            ("Region Skåne", 297),           # 4h57m -- longest
            ("Region Uppsala", 289),         # 4h49m
            ("Region Jönköpings län", 182),  # 3h2m -- shortest
        ],
    )

    # ---------------- Hospital snapshot, 2025 (time to first doctor) ----------------
    cur.execute("""
        CREATE TABLE er_hospital_2025 (
            hospital TEXT PRIMARY KEY,
            median_time_to_doctor_minutes INTEGER
        )
    """)
    cur.executemany(
        "INSERT INTO er_hospital_2025 VALUES (?, ?)",
        [
            ("Södra Älvsborgs sjukhus", 98),
            ("Växjö sjukhus", 84),
            ("Sunderby sjukhus", 84),
            ("Skånes universitetssjukhus Malmö", 82),
            ("Nya Karolinska Solna", 29),
            ("Gällivare sjukhus", 30),
            ("Kiruna sjukhus", 25),
            ("Kalix sjukhus", 19),
        ],
    )

    # ---------------- Demographic gap (real published pattern) ----------------
    cur.execute("""
        CREATE TABLE er_demographic_notes (
            note_id INTEGER PRIMARY KEY,
            year INTEGER,
            description TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO er_demographic_notes (year, description) VALUES (?, ?)",
        [
            (2024, "Women aged 19-79 had a median total stay of 4h 7m (247 minutes) in 2024."),
            (2024, "Women over 80 had the longest average time of any group in the emergency department, a consistent pattern across years."),
            (2025, "Women waited on average about 9 minutes longer in total stay time than men, a gap that has been consistent for many years."),
        ],
    )

    # ---------------- Specialist care summary, 2024 (national) ----------------
    cur.execute("""
        CREATE TABLE specialist_care_summary_2024 (
            metric TEXT PRIMARY KEY,
            value INTEGER,
            note TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO specialist_care_summary_2024 VALUES (?, ?, ?)",
        [
            ("total_patients_in_specialist_care", 4_443_000, "People hospitalized or seen in specialist outpatient care in 2024"),
            ("total_hospital_admissions", 1_377_000, "Total inpatient admissions to Swedish hospitals in 2024"),
            ("disease_symptom_admissions", 1_064_000, "Admissions specifically for disease/symptom diagnoses (subset of total)"),
            ("total_hospitalized_patients", 824_000, "Unique patients hospitalized (not admission count) in 2024"),
        ],
    )

    # ---------------- ICD-10 chapter reference (standard classification) ----------------
    cur.execute("""
        CREATE TABLE icd10_chapters (
            chapter_code TEXT PRIMARY KEY,
            code_range TEXT,
            chapter_name_en TEXT,
            chapter_name_sv TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO icd10_chapters VALUES (?, ?, ?, ?)",
        [
            ("I",    "A00-B99", "Certain infectious and parasitic diseases", "Vissa infektionssjukdomar och parasitsjukdomar"),
            ("II",   "C00-D48", "Neoplasms (cancers)", "Tumörer"),
            ("IX",   "I00-I99", "Diseases of the circulatory system", "Cirkulationsorganens sjukdomar"),
            ("X",    "J00-J99", "Diseases of the respiratory system", "Andningsorganens sjukdomar"),
            ("XI",   "K00-K93", "Diseases of the digestive system", "Matsmältningsorganens sjukdomar"),
            ("XIII", "M00-M99", "Diseases of the musculoskeletal system and connective tissue", "Sjukdomar i muskuloskeletala systemet och bindväven"),
            ("XIV",  "N00-N99", "Diseases of the genitourinary system", "Urin- och könsorganens sjukdomar"),
            ("XIX",  "S00-T98", "Injury, poisoning and certain other consequences of external causes", "Skador, förgiftningar och vissa andra följder av yttre orsaker"),
        ],
    )

    # ---------------- Top admission cause by sex, 2024 (real reported headline) ----------------
    cur.execute("""
        CREATE TABLE top_admission_cause_2024 (
            sex TEXT PRIMARY KEY,
            top_icd10_chapter_code TEXT,
            note TEXT,
            FOREIGN KEY (top_icd10_chapter_code) REFERENCES icd10_chapters(chapter_code)
        )
    """)
    cur.executemany(
        "INSERT INTO top_admission_cause_2024 VALUES (?, ?, ?)",
        [
            ("Male", "IX", "Cardiovascular disease was the most common reason for hospital admission among men in 2024."),
        ],
    )

    conn.commit()
    conn.close()
    print(f"Database built at {DB_PATH}")


if __name__ == "__main__":
    build_database()

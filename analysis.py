"""
SQL analysis layer for the Swedish Healthcare Statistics project.

This module deliberately writes raw SQL queries (rather than only using
pandas) to demonstrate SQL skills directly -- this mirrors how analysts at
agencies like Socialstyrelsen actually work with their statistics
databases, often querying register data directly via SQL/SAS before any
further analysis or visualization.

R -> SQL note for reference: dplyr's `filter() %>% group_by() %>% summarize()`
maps onto SQL's `WHERE ... GROUP BY ... SELECT AGG(...)` -- the same logical
steps, different syntax.
"""

import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "healthcare_stats.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def national_trend() -> pd.DataFrame:
    """Yearly national ER waiting time trend."""
    query = """
        SELECT year,
               total_visits,
               median_total_stay_minutes,
               median_time_to_doctor_minutes
        FROM er_national_yearly
        ORDER BY year ASC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def region_ranking() -> pd.DataFrame:
    """Regions ranked by total ER stay time, longest first."""
    query = """
        SELECT region,
               median_total_stay_minutes,
               ROUND(median_total_stay_minutes / 60.0, 1) AS median_total_stay_hours
        FROM er_region_2025
        ORDER BY median_total_stay_minutes DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def hospital_extremes(n: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Slowest and fastest hospitals for time-to-doctor, using SQL's
    ORDER BY + LIMIT instead of doing the sort/slice in Python.
    """
    slowest_query = f"""
        SELECT hospital, median_time_to_doctor_minutes
        FROM er_hospital_2025
        ORDER BY median_time_to_doctor_minutes DESC
        LIMIT {n}
    """
    fastest_query = f"""
        SELECT hospital, median_time_to_doctor_minutes
        FROM er_hospital_2025
        ORDER BY median_time_to_doctor_minutes ASC
        LIMIT {n}
    """
    with get_connection() as conn:
        slowest = pd.read_sql_query(slowest_query, conn)
        fastest = pd.read_sql_query(fastest_query, conn)
    return slowest, fastest


def specialist_care_summary() -> pd.DataFrame:
    query = "SELECT metric, value, note FROM specialist_care_summary_2024"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def icd10_chapters() -> pd.DataFrame:
    query = """
        SELECT chapter_code, code_range, chapter_name_en, chapter_name_sv
        FROM icd10_chapters
        ORDER BY chapter_code
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def top_admission_causes() -> pd.DataFrame:
    """
    Demonstrates a SQL JOIN -- linking the top-admission-cause table to the
    ICD-10 chapter reference table, rather than matching them manually in
    pandas after the fact.
    """
    query = """
        SELECT t.sex,
               c.chapter_code,
               c.chapter_name_en,
               t.note
        FROM top_admission_cause_2024 t
        JOIN icd10_chapters c ON t.top_icd10_chapter_code = c.chapter_code
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def demographic_notes(year: int | None = None) -> pd.DataFrame:
    query = "SELECT year, description FROM er_demographic_notes"
    params = ()
    if year is not None:
        query += " WHERE year = ?"
        params = (year,)
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def yoy_change(df: pd.DataFrame, value_col: str) -> float:
    """Year-over-year percent change between first and last row."""
    df = df.sort_values("year")
    first, last = df[value_col].iloc[0], df[value_col].iloc[-1]
    if first == 0:
        return 0.0
    return round((last - first) / first * 100, 1)

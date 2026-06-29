"""
Swedish Healthcare Statistics Dashboard -- Streamlit app.

Run with:
    streamlit run app.py
"""

import streamlit as st
import plotly.express as px

import analysis as a

st.set_page_config(page_title="Swedish Healthcare Statistics", page_icon="🇸🇪", layout="wide")

st.title("🇸🇪 Swedish Healthcare Statistics Dashboard")
st.caption(
    "Emergency department waiting-time statistics and ICD-10 diagnosis data, modeled on the "
    "kind of register-based statistics Socialstyrelsen (Sweden's National Board of Health and "
    "Welfare) publishes from the National Patient Register. Built with SQLite + SQL queries, "
    "pandas, and Plotly."
)

with st.expander("ℹ️ About this data"):
    st.markdown(
        "All figures are real, published statistics from Socialstyrelsen's official reports "
        "on emergency department visits and waiting times (2023-2025) and specialist care "
        "(2024), plus the standard ICD-10 chapter classification. See README for full source "
        "details, including which specific figures were back-calculated from a published "
        "percentage change rather than published directly."
    )

st.sidebar.title("🇸🇪 Healthcare Stats")
view = st.sidebar.radio(
    "What do you want to explore?",
    [
        "National trend over time",
        "Regional comparison",
        "Hospital-level extremes",
        "ICD-10 diagnosis chapters",
        "Specialist care summary",
    ],
)

st.markdown("---")

if view == "National trend over time":
    st.subheader("Emergency department waiting times — national trend")
    df = a.national_trend()

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.line(
            df, x="year", y="median_total_stay_minutes", markers=True,
            labels={"median_total_stay_minutes": "Minutes"},
            title="Median total time spent in the ER",
        )
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.line(
            df, x="year", y="median_time_to_doctor_minutes", markers=True,
            labels={"median_time_to_doctor_minutes": "Minutes"},
            title="Median time to see a doctor",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

    change = a.yoy_change(df, "median_total_stay_minutes")
    st.info(
        f"Median total ER stay time changed by {change:+.1f}% between {df['year'].iloc[0]} and "
        f"{df['year'].iloc[-1]}. Total visit counts for 2023 and 2025 are estimated from "
        f"published year-over-year percentage changes (flagged in the database)."
    )

    with st.expander("View SQL query used"):
        st.code(
            "SELECT year, total_visits, median_total_stay_minutes, median_time_to_doctor_minutes\n"
            "FROM er_national_yearly\nORDER BY year ASC",
            language="sql",
        )

elif view == "Regional comparison":
    st.subheader("ER total stay time by region (2025 snapshot)")
    df = a.region_ranking()

    fig = px.bar(
        df, x="region", y="median_total_stay_hours",
        labels={"median_total_stay_hours": "Median total stay (hours)"},
        title="Median total ER stay time by region, 2025",
        color="median_total_stay_hours", color_continuous_scale="Reds",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info(
        f"{df.iloc[0]['region']} had the longest median stay at {df.iloc[0]['median_total_stay_hours']} hours, "
        f"compared to {df.iloc[-1]['region']} at {df.iloc[-1]['median_total_stay_hours']} hours — "
        f"a difference of {df.iloc[0]['median_total_stay_minutes'] - df.iloc[-1]['median_total_stay_minutes']} minutes."
    )

    with st.expander("View SQL query used"):
        st.code(
            "SELECT region, median_total_stay_minutes,\n"
            "       ROUND(median_total_stay_minutes / 60.0, 1) AS median_total_stay_hours\n"
            "FROM er_region_2025\nORDER BY median_total_stay_minutes DESC",
            language="sql",
        )

    st.markdown("#### Demographic notes")
    notes = a.demographic_notes()
    for _, row in notes.iterrows():
        st.markdown(f"- **{row['year']}**: {row['description']}")

elif view == "Hospital-level extremes":
    st.subheader("Time to see a doctor — slowest vs. fastest hospitals (2025)")
    slowest, fastest = a.hospital_extremes()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🐢 Slowest (longest wait)**")
        fig_slow = px.bar(
            slowest, x="hospital", y="median_time_to_doctor_minutes",
            labels={"median_time_to_doctor_minutes": "Minutes"}, color_discrete_sequence=["#d62728"],
        )
        st.plotly_chart(fig_slow, use_container_width=True)
    with col2:
        st.markdown("**🐇 Fastest (shortest wait)**")
        fig_fast = px.bar(
            fastest, x="hospital", y="median_time_to_doctor_minutes",
            labels={"median_time_to_doctor_minutes": "Minutes"}, color_discrete_sequence=["#2ca02c"],
        )
        st.plotly_chart(fig_fast, use_container_width=True)

    with st.expander("View SQL queries used"):
        st.code(
            "-- Slowest:\n"
            "SELECT hospital, median_time_to_doctor_minutes\nFROM er_hospital_2025\n"
            "ORDER BY median_time_to_doctor_minutes DESC LIMIT 4\n\n"
            "-- Fastest:\n"
            "SELECT hospital, median_time_to_doctor_minutes\nFROM er_hospital_2025\n"
            "ORDER BY median_time_to_doctor_minutes ASC LIMIT 4",
            language="sql",
        )

elif view == "ICD-10 diagnosis chapters":
    st.subheader("ICD-10 diagnosis chapter reference")
    df = a.icd10_chapters()
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Top admission cause by sex (2024) — via SQL JOIN")
    joined = a.top_admission_causes()
    for _, row in joined.iterrows():
        st.markdown(
            f"- **{row['sex']}**: Chapter {row['chapter_code']} — {row['chapter_name_en']}. {row['note']}"
        )

    with st.expander("View SQL query used (JOIN)"):
        st.code(
            "SELECT t.sex, c.chapter_code, c.chapter_name_en, t.note\n"
            "FROM top_admission_cause_2024 t\n"
            "JOIN icd10_chapters c ON t.top_icd10_chapter_code = c.chapter_code",
            language="sql",
        )

elif view == "Specialist care summary":
    st.subheader("Specialist care summary, 2024 (national)")
    df = a.specialist_care_summary()

    cols = st.columns(len(df))
    for col, (_, row) in zip(cols, df.iterrows()):
        col.metric(row["metric"].replace("_", " ").title(), f"{row['value']:,}")

    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("View SQL query used"):
        st.code("SELECT metric, value, note FROM specialist_care_summary_2024", language="sql")

st.markdown("---")
st.caption(
    "Data sourced from Socialstyrelsen's official statistics on emergency department visits "
    "and waiting times (2023-2025) and specialist care (2024). ICD-10 chapter structure follows "
    "the standard WHO classification (ICD-10-SE in Sweden). See README for full provenance notes."
)

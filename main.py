import threading
import schedule
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Import the scraper function from your scripts folder.
from scripts.pharma_scraper import run_scraper
# Import analysis functions from analyzer.py for the remaining tabs.
from scripts.analyzer import (
    load_profiles, 
    categorize_job_areas, 
    extract_tools_and_certificates, 
    summarize_trends, 
    create_bar_chart
)

# ---------------------------
# Background Scraper Scheduler
# ---------------------------
def run_scraper_scheduler():
    # Schedule the scraper to run daily at 23:59.
    schedule.every().day.at("23:59").do(run_scraper)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scraper scheduler in a background thread.
threading.Thread(target=run_scraper_scheduler, daemon=True).start()

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Biopharma Analyzer", layout="wide")
st.title("Biopharma Job Profile Analyzer")


profiles, df = load_profiles()

if profiles:
    st.write("### Job Data")
    st.dataframe(df, use_container_width=True)

    # Create tabs for various analyses (without AI Insights).
    tab1, tab2, tab3, tab4 = st.tabs([
        "Job Areas", "Tools", "Certificates", "Trends"
    ])

    with tab1:
        st.subheader("Job Area Analysis")
        job_areas = categorize_job_areas(profiles)
        st.plotly_chart(create_bar_chart(job_areas, "Job Area Analysis"))

    with tab2:
        st.subheader("Tools Mentioned")
        tools_counts, _ = extract_tools_and_certificates(profiles)
        st.plotly_chart(create_bar_chart(tools_counts, "Tools Mentioned"))

    with tab3:
        st.subheader("Certificates Mentioned")
        _, certificates_counts = extract_tools_and_certificates(profiles)
        st.plotly_chart(create_bar_chart(certificates_counts, "Certificates Mentioned"))

    with tab4:
        st.subheader("Trends for Upskilling")
        trends = summarize_trends(profiles)
        st.plotly_chart(create_bar_chart(trends, "Trends for Upskilling"))
else:
    st.warning("No profiles found. Please ensure the CSV file has been generated.")

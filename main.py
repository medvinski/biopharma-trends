import streamlit as st
from collections import Counter
import pandas as pd
import plotly.express as px


# Helper functions
def load_profiles(csv_file="data/title_profile.csv"):
    """Load job profiles from CSV."""
    try:
        df = pd.read_csv(csv_file)
        return df["Profile"].dropna().tolist(), df
    except FileNotFoundError:
        st.error(f"File '{csv_file}' not found.")
        return [], None


def categorize_job_areas(profiles):
    """Categorize jobs into predefined areas based on keywords."""
    areas = {
        "Clinical": ["clinical", "trials", "patients", "medicine"],
        "Regulatory": ["regulatory", "compliance", "gcp", "fda", "guidelines"],
        "Data Analysis": ["data", "analysis", "statistics", "programming", "sql", "python", "R"],
        "Biotechnology": ["biotech", "biotechnology", "biologics", "pharmaceutical"],
        "AI and Machine Learning": ["ai", "machine learning", "deep learning", "nlp", "automation", "mlops"],
        "Management": ["management", "leadership", "project"],
        "Manufacturing": ["manufacturing", "production", "quality", "cmc"]
    }

    area_counts = Counter()
    for profile in profiles:
        for area, keywords in areas.items():
            if any(keyword in profile.lower() for keyword in keywords):
                area_counts[area] += 1

    return area_counts


def extract_tools_and_certificates(profiles):
    """Extract tools and certificates from job profiles, avoiding false positives."""
    tools = [
        # Pharma-Specific Tools
        'veeva', 'sas', 'sql', 'python', 'r programming', 'R', 'java', 'excel', 'tableau', 'powerpoint',
        'jira', 'masshunter', 'spotfire', 'knime', 'minitab', 'biovia', 'chromeleon',
        'lims', 'cdms', 'edc', 'medidata', 'argus', 'oracle', 'sap', 'qlik', 'spss',
        'clinicaltrialsgov', 'microsoft project', 'prism',
        # Marketing and Business Tools
        'salesforce', 'google analytics', 'hubspot', 'adobe marketing cloud', 'mailchimp',
        # Data Analysis and IT Tools
        'power bi', 'sql server', 'numpy', 'pandas', 'tensorflow', 'keras', 'matplotlib', 'seaborn',
        'hadoop', 'spark', 'bigquery', 'snowflake', 'databricks', 'apache airflow', 'rapidminer',
        # AI and Machine Learning Tools
        'scikit-learn', 'huggingface', 'openai', 'nlp', 'machine learning', 'deep learning',
        'bert', 'gpt', 'mlflow', 'pytorch', 'transformers'
    ]

    certificates = [
        # Pharma-Specific Certificates
        'gcp', 'gmp', 'rac', 'pharmacovigilance certification', 'pharmd', 'msc', 'msc pharm', 'lean',
        'ich', 'md', 'capm', 'cqia', 'clinical research certification', 'certified regulatory affairs professional',
        'good manufacturing practices', 'quality by design', 'qbd',
        # IT/Business Certificates
        'pmp', 'six sigma', 'scrum master', 'aws certified', 'sas certified', 'google data analytics',
        'azure data engineer', 'certified data scientist', 'digital marketing certification',
        'facebook blueprint', 'aws solutions architect', 'iso 9001', 'lean six sigma',
        # AI/ML Certificates
        'machine learning certification', 'deep learning certification', 'ai certification',
        'certified data engineer', 'certified mlops engineer'
    ]

    tools_counts = Counter()
    certificates_counts = Counter()

    for profile in profiles:
        words = profile.lower().split()  # Split the profile into words for precise matching

        for tool in tools:
            # Match tools only as standalone words or phrases
            if any(word.strip() == tool.lower() for word in words):
                tools_counts[tool] += 1

        for cert in certificates:
            # Match certificates only as standalone words or phrases
            if any(word.strip() == cert.lower() for word in words):
                certificates_counts[cert] += 1

    return tools_counts, certificates_counts


def summarize_trends(profiles):
    """Generate a summary of meaningful trends across all job profiles."""
    practical_phrases = [
        "communication skills", "team management", "leadership skills", "clinical trials",
        "regulatory compliance", "biotechnology expertise", "data analysis", "project management",
        "drug development", "statistical analysis", "quality assurance", "manufacturing processes",
        "machine learning expertise", "ai experience", "automation", "nlp"
    ]

    trend_counts = Counter()
    for profile in profiles:
        for phrase in practical_phrases:
            if phrase in profile.lower():
                trend_counts[phrase] += 1

    return trend_counts


# Helper function to create sorted bar charts
def create_bar_chart(data, title):
    """Create a readable bar chart using Plotly, sorted by values in descending order."""
    df = pd.DataFrame.from_dict(data, orient="index", columns=["Count"]).reset_index()
    df.columns = ["Category", "Count"]
    df = df.sort_values(by="Count", ascending=False)  # Sort data by count
    fig = px.bar(
        df,
        x="Category",
        y="Count",
        title=title,
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-45,  # Rotate x-axis labels
        xaxis_title=None,
        yaxis_title="Count",
        margin=dict(l=40, r=40, t=40, b=80),  # Adjust margins
        font=dict(size=12),  # Adjust font size
    )
    return fig


# Streamlit App
st.set_page_config(page_title="Pharma Job Profile Analyzer", layout="wide")
st.title("Pharma Job Profile Analyzer")

# Load and Display Data
st.write("### Load Profiles from CSV")
profiles, df = load_profiles()

if profiles:
    st.write("### Job Data")
    st.dataframe(df, use_container_width=True)

    # Use Tabs for Organizing Sections
    tab1, tab2, tab3, tab4 = st.tabs(["Job Areas", "Tools", "Certificates", "Trends"])

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
    st.warning("No profiles found. Please upload a valid CSV file.")

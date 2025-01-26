from collections import Counter
import pandas as pd


def load_profiles(csv_file="data/title_profile.csv"):
    """Load job profiles from CSV."""
    try:
        df = pd.read_csv(csv_file)
        return df["Profile"].dropna().tolist(), df
    except FileNotFoundError:
        print(f"File '{csv_file}' not found.")
        return [], None


def categorize_job_areas(profiles):
    """Categorize jobs into predefined areas based on keywords."""
    areas = {
        "Clinical": ["clinical", "trials", "patients", "medicine"],
        "Regulatory": ["regulatory", "compliance", "gcp", "fda", "guidelines"],
        "Data Analysis": ["data", "analysis", "statistics", "programming", "sql", "python", "r"],
        "Biotechnology": ["biotech", "biotechnology", "biologics", "pharmaceutical"],
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
    """Extract tools and certificates from job profiles."""
    # Expanded list of tools relevant to the pharma industry
    tools = [
        'veeva', 'sas', 'sql', 'python', 'r', 'java', 'excel', 'tableau', 'powerpoint',
        'jira', 'masshunter', 'spotfire', 'knime', 'minitab', 'biovia', 'chromeleon',
        'lims', 'cdms', 'edc', 'medidata', 'argus', 'oracle', 'sap', 'qlik', 'spss',
        'clinicaltrialsgov', 'microsoft project', 'prism'
    ]

    # Expanded list of certifications relevant to the pharma industry
    certificates = [
        'pmp', 'six sigma', 'cmc', 'gcp', 'fda', 'iso', 'pharmacovigilance', 'pharmd', 'mba', 'phd',
        'lean', 'scrum master', 'ich', 'md', 'msc', 'msc pharm', 'capm', 'cqia', 'rac', 'cpim',
        'cspo', 'cisa', 'clinical research certification', 'certified regulatory affairs professional',
        'good manufacturing practices', 'gmp', 'quality by design', 'qbd'
    ]

    tools_counts = Counter()
    certificates_counts = Counter()

    for profile in profiles:
        for tool in tools:
            if tool in profile.lower():
                tools_counts[tool] += 1
        for cert in certificates:
            if cert in profile.lower():
                certificates_counts[cert] += 1

    return tools_counts, certificates_counts


def summarize_trends(profiles):
    """Generate a summary of meaningful trends across all job profiles."""
    practical_phrases = [
        "communication skills", "team management", "leadership skills", "clinical trials",
        "regulatory compliance", "biotechnology expertise", "data analysis", "project management",
        "drug development", "statistical analysis", "quality assurance", "manufacturing processes"
    ]

    trend_counts = Counter()
    for profile in profiles:
        for phrase in practical_phrases:
            if phrase in profile.lower():
                trend_counts[phrase] += 1

    return trend_counts


def analyze_profiles(csv_file="data/title_profile.csv"):
    """Analyze profiles and provide insights."""
    profiles, df = load_profiles(csv_file)
    if not profiles:
        return

    print("\nJob Area Analysis:")
    job_areas = categorize_job_areas(profiles)
    for area, count in job_areas.items():
        print(f"{area}: {count} jobs")

    print("\nTools and Certificates Mentioned:")
    tools_counts, certificates_counts = extract_tools_and_certificates(profiles)

    print("\nTools:")
    for tool, count in tools_counts.items():
        print(f"{tool}: {count}")

    print("\nCertificates:")
    for cert, count in certificates_counts.items():
        print(f"{cert}: {count}")

    print("\nSummary of Meaningful Trends for Upskilling:")
    trends = summarize_trends(profiles)
    for trend, count in trends.items():
        print(f"{trend}: {count}")


if __name__ == "__main__":
    analyze_profiles()

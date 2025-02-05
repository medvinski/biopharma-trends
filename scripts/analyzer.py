from collections import Counter
import pandas as pd
import re
import plotly.express as px
import difflib

def load_profiles(csv_file="data/title_profile.csv"):
    """Wczytuje profile ofert pracy z pliku CSV."""
    try:
        df = pd.read_csv(csv_file)
        return df["Profile"].dropna().tolist(), df
    except FileNotFoundError:
        print(f"File '{csv_file}' not found.")
        return [], None

def categorize_job_areas(profiles):
    """
    Kategoryzuje oferty pracy do określonych obszarów na podstawie słów kluczowych,
    przy czym dla przypisania profilu do danej kategorii wymagane jest wystąpienie co najmniej dwóch słów kluczowych.
    
    Łączy kategorie 'Clinical' i 'Biotechnology' w jedną, ponieważ często dotyczą one podobnych obszarów badań i rozwoju.
    """
    areas = {
        "Clinical & Biotechnology R&D": [
            "clinical", "trials", "research"
        ],
        "Regulatory": [
            "regulatory", "compliance", "fda", "emea"
        ],
        "Data Analysis": [
            "data", "analysis", "statistics", "programming", "sql", "python", "r", "big data"
        ],
        "Management": [
            "management", "leadership", "project", "project management", "change management"
        ],
        "Manufacturing": [
            "manufacturing", "production", "quality", "cmc"
        ],
        "Marketing/Digital": [
            "marketing", "digital", "seo", "sem", "social media", "content", "campaign"
        ],
        "AI": [
            "ai", "artificial intelligence", "machine learning", "deep learning", "neural networks"
        ]
    }
    
    area_counts = Counter()
    for profile in profiles:
        lower_profile = profile.lower()
        for area, keywords in areas.items():
            match_count = 0
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, lower_profile):
                    match_count += 1
            # Przypisujemy profil do danej kategorii, jeżeli znaleziono co najmniej 2 słowa kluczowe
            if match_count >= 2:
                area_counts[area] += 1
    return area_counts

def extract_tools_and_certificates(profiles):
    """
    Ekstrahuje z profili oferty pracy informacje o narzędziach i certyfikatach,
    korzystając z dopasowań wyrażeń regularnych (regex).
    """
    tools = [
        'veeva', 'sas', 'sql', 'python', 'r', 'java', 'excel', 'tableau', 'powerpoint',
        'jira', 'masshunter', 'spotfire', 'knime', 'minitab', 'biovia', 'chromeleon',
        'lims', 'cdms', 'edc', 'medidata', 'argus', 'oracle', 'sap', 'qlik', 'spss',
        'clinicaltrialsgov', 'microsoft project', 'prism', 'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'hadoop', 'spark', 'aws', 'azure', 'google cloud', 'power bi',
        'adobe analytics', 'google analytics', 'hubspot', 'marketo', 'salesforce', 'aem'
    ]
    certificates = [
        'pmp', 'six sigma', 'cmc', 'gcp', 'iso', 'pharmacovigilance',
        'lean', 'scrum master', 'ich', 'capm', 'cqia', 'rac', 'cpim',
        'cspo', 'cisa', 'good manufacturing practices', 'gmp', 'quality by design', 'qbd',
        'google ads', 'google analytics', 'hubspot', 'salesforce',
        'aws', 'azure', 'tensorflow', 'pmi-acp'
    ]
    # Usunięcie duplikatów z listy certyfikatów.
    certificates = list(dict.fromkeys(certificates))

    tools_counts = Counter()
    certificates_counts = Counter()

    for profile in profiles:
        lower_profile = profile.lower()
        for tool in tools:
            pattern = r'\b' + re.escape(tool) + r'\b'
            if re.search(pattern, lower_profile):
                tools_counts[tool] += 1
        for cert in certificates:
            pattern = r'\b' + re.escape(cert) + r'\b'
            if re.search(pattern, lower_profile):
                certificates_counts[cert] += 1

    return tools_counts, certificates_counts

def summarize_trends(profiles):
    """
    Generuje podsumowanie istotnych trendów występujących w profilach ofert pracy,
    wykorzystując zarówno dokładne dopasowania za pomocą regex, jak i fuzzy matching do wykrywania podobnych fraz.
    """
    practical_phrases = [
        # Kluczowe umiejętności miękkie i związane z zarządzaniem
        "communication skills",
        "team management",
        "leadership skills",
        "project management",
        "agile methodology",
        "agile",
        "customer engagement",
        "data-driven decision making",
        
        # Specyficzne dla branży i techniczne frazy
        "clinical trials",
        "regulatory compliance",
        "biotechnology expertise",
        "drug development",
        "statistical analysis",
        "quality assurance",
        "manufacturing processes",
        "supply chain optimization",
        "pharmacovigilance",
        
        # Trendy związane z transformacją cyfrową i technologiami IT
        "digital transformation",
        "digital marketing",
        "big data analytics",
        "predictive analytics",
        "cloud computing",
        "automation",
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "ai implementation",
        "machine learning models",
        "neural networks",
        "internet of things",
        "blockchain",
        "cybersecurity",
        "edge computing",
        "robotics process automation",
        "rpa",
        "data science",
        "data engineering"
    ]
    
    trend_counts = Counter()
    for profile in profiles:
        lower_profile = profile.lower()
        # Podziel tekst na zdania, aby lepiej wykrywać podobne frazy.
        sentences = re.split(r'[.!?]', lower_profile)
        for phrase in practical_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            # Sprawdzenie dokładnego dopasowania w całym profilu
            if re.search(pattern, lower_profile):
                trend_counts[phrase] += 1
            else:
                # Jeśli brak dokładnego dopasowania, sprawdzamy każde zdanie przy użyciu fuzzy matching
                for sentence in sentences:
                    if difflib.get_close_matches(phrase, [sentence], n=1, cutoff=0.8):
                        trend_counts[phrase] += 1
                        break
    return trend_counts

def create_bar_chart(data, title):
    """Tworzy czytelny wykres słupkowy przy użyciu Plotly, sortując dane malejąco według wartości."""
    df = pd.DataFrame.from_dict(data, orient="index", columns=["Count"]).reset_index()
    df.columns = ["Category", "Count"]
    df = df.sort_values(by="Count", ascending=False)
    fig = px.bar(
        df,
        x="Category",
        y="Count",
        title=title,
        text="Count"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title=None,
        yaxis_title="Count",
        margin=dict(l=40, r=40, t=40, b=80),
        font=dict(size=12)
    )
    return fig

def analyze_profiles(csv_file="data/title_profile.csv"):
    """Analizuje profile ofert pracy oraz wypisuje wyniki analizy."""
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

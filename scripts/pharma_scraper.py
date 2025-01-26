import requests
from bs4 import BeautifulSoup
import csv
import os

# Base URL for EuroPharmaJobs (specific category search link)
BASE_URL = "https://www.europharmajobs.com/job_search/category/bioinformatics/category/biotechnology_and_genetics/category/clinical_data_management/category/clinical_research/category/data_programming_and_statistics/category/manufacturing_and_logistics/category/medical/category/medical_devices/category/pharmacovigilance_and_medical_information/category/pre-clinical_research_and_development/category/programming/category/quality_assurance/category/regulatory_affairs/category/sales_marketing_and_communications/category/statistics"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def get_job_links():
    """Get the job listing links from the search results."""
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    job_links = []
    for job in soup.find_all("a", href=True):
        if "job_display" in job["href"]:  # Find job listing links
            job_url = f"https://www.europharmajobs.com/{job['href']}"
            if job_url not in job_links:  # Avoid duplicates
                job_links.append(job_url)
    return job_links

def scrape_job_profile(job_url):
    """Scrape the Profile section of the job listing."""
    response = requests.get(job_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract job title
    job_title_element = soup.find("h1")
    job_title = job_title_element.text.strip() if job_title_element else "N/A"

    # Extract Profile section based on different possible headers
    headers = [
        "Qualifications",
        "Your experience and qualifications",
        "About you",
        "Profile",
        "What you’ll bring to the role:",
        "Job requirements",
        "Education, Skills and Experience:",
        "Qualifications:",
        "Knowledge and Experience",
        "What you will bring to the role",
        "Other Information/Additional Preferences:"
    ]

    qualifications_content = ""
    for header in headers:
        qualifications_element = soup.find("h3", string=lambda text: text and text.lower().startswith(header.lower().strip(':')))
        if qualifications_element:
            for sibling in qualifications_element.find_next_siblings():
                if sibling.name == "a" and "Apply Now" in sibling.text:
                    break  # Stop when reaching the Apply Now button
                if "Share this Job" in sibling.text or "Don't forget to mention" in sibling.text or "Apply Now" in sibling.text:
                    continue  # Skip unwanted content
                qualifications_content += sibling.text.strip() + "\n"
            break  # Exit loop once a valid header is found

    return {
        "Job Title": job_title,
        "Profile": qualifications_content.strip()
    }

def save_profiles_to_csv(job_data_list, filename="data/title_profile.csv"):
    """Save job profile data to a CSV file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Job Title", "Profile"])
        for job_data in job_data_list:
            writer.writerow([job_data["Job Title"], job_data["Profile"]])

if __name__ == "__main__":
    job_links = get_job_links()
    if job_links:
        print(f"Found {len(job_links)} job listings.")
        job_profiles = []

        for job_url in job_links:  # Process all job listings
            print(f"Scraping job listing: {job_url}")
            job_data = scrape_job_profile(job_url)
            job_profiles.append(job_data)  # Append each job's data

        # Overwrite the CSV file with updated content
        save_profiles_to_csv(job_profiles)

        print(f"Scraping completed. Profiles saved to 'data/title_profile.csv'.")
    else:
        print("No job listings found.")

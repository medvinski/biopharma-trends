import requests                          
from bs4 import BeautifulSoup             
import csv                               
import os                                 
import time                               
import logging                           
import schedule                           
import difflib                            
import re                                 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adres URL głównej strony z ofertami pracy, z której będą pobierane dane.
BASE_URL = (
    "https://www.europharmajobs.com/job_search/category/bioinformatics/"
    "category/biotechnology_and_genetics/category/clinical_data_management/"
    "category/clinical_research/category/data_programming_and_statistics/"
    "category/manufacturing_and_logistics/category/medical/category/medical_devices/"
    "category/pharmacovigilance_and_medical_information/category/pre-clinical_research_and_development/"
    "category/programming/category/quality_assurance/category/regulatory_affairs/"
    "category/sales_marketing_and_communications/category/statistics"
)

# Imitacja przeglądarki, aby uniknąć blokady.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def get_job_links(session):
    
    try:
        response = session.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()  
    except requests.RequestException as e:
        logging.error(f"Error fetching main page: {e}")
        return []
    
    
    soup = BeautifulSoup(response.text, "html.parser")
    job_links = []
    
    for job in soup.find_all("a", href=True):
        
        if "job_display" in job["href"]:
            job_url = f"https://www.europharmajobs.com/{job['href']}"
            if job_url not in job_links:
                job_links.append(job_url)
    return job_links

def filter_unwanted(text):
   
    lines = text.splitlines()  
    filtered = []
    for line in lines:
        low_line = line.strip().lower()  
        
        if "apply now" in low_line:
            break
        if "jobs by experience" in low_line:
            break
        filtered.append(line.strip())
    return "\n".join(filtered)

def scrape_job_profile(session, job_url):
   
    try:
        response = session.get(job_url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching job listing {job_url}: {e}")
        return {"Job Title": "N/A", "Profile": None}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
   
    job_title_element = soup.find("h1")
    job_title = job_title_element.text.strip() if job_title_element else "N/A"
    
    
    container = soup.find("div", class_="jobDisplay")
    if not container:
        container = soup  

   
    header_keywords = [
        "qualifications and skills:",
        "key competencies:",
        "who you are?",
        "profile",
        "what you’ll bring to the role:",
        "desirable requirements:",
        "what we expect of you",
        "minimum requirements:",
        "knowledge, skills and abilities:",
        "who we are looking for",
        "person specification",
        "required skills and experience",
        "hands-on qa experience and networking skills",
        "who we are looking for:",
        "education / certifications:",
        "key requirements:",
        "for this role you will need:",
        "we are looking to recruit a candidate:",
        "your background",
        "to be successful in the role, you will have:",
        "knowledge, experience and skills:",
        "what you will bring:",
        "what you’ll bring",
        "requirements",
        "main areas of responsibility:",
        "skills and experience",
        "you must have:",
        "basic requirements:",
        "what will you need to be successful?",
        "skills & experiences",
        "key competencies",
        "your experience/acknowledgment:",
        "experience",
        "experience required",
        "what do you need to be successful?",
        "education & experience",
        "behind our innovation…there’s you",
        "additional skills/preferences:",
        "what are we looking for in you?",
        "you are:",
        "what we look for",
        "experience requirements:",
        "key competency requirements",
        "experience and skills",
        "candidate criteria",
        "essential requirements:",
        "what you'll bring to the table",
        "requirements for the role include:",
        "skills and additional requirements",
        "attributes for the role",
        "educational requirements",
        "attributes for the role:"
    ]
    
    header_keywords = [k.strip().lower() for k in header_keywords]

    extracted_content = ""
    
    for header_element in container.find_all("h3"):
        header_text = header_element.get_text(separator=" ", strip=True).lower()
        
        if "jobs by experience" in header_text:
            continue
        
        if any(keyword in header_text for keyword in header_keywords) or \
           difflib.get_close_matches(header_text, header_keywords, n=1, cutoff=0.8):
            section_text = ""
            
            for sibling in header_element.find_next_siblings():
                sibling_text = sibling.get_text(separator=" ", strip=True)
                
                if "apply now" in sibling_text.lower():
                    break
                section_text += sibling_text + "\n"
            extracted_content += section_text + "\n"
    
    
    profile = filter_unwanted(extracted_content.strip()) if extracted_content.strip() else None

    return {
        "Job Title": job_title,
        "Profile": profile
    }

def save_profiles_to_csv(job_data_list, filename="data/title_profile.csv"):
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Job Title", "Profile"])
        writer.writeheader()
        for job_data in job_data_list:
            writer.writerow(job_data)

def run_scraper():
  
    with requests.Session() as session:
        job_links = get_job_links(session)
        if not job_links:
            logging.info("No job listings found.")
            return
        
        logging.info(f"Found {len(job_links)} job listings.")
        job_profiles = []
        for job_url in job_links:
            logging.info(f"Scraping job listing: {job_url}")
            job_data = scrape_job_profile(session, job_url)
            if job_data["Profile"] is not None:
                job_profiles.append(job_data)
            else:
                logging.info(f"Skipping job listing {job_url} due to no profile data.")
            time.sleep(1)  # Krótkie opóźnienie, aby nie przeciążać serwera
        save_profiles_to_csv(job_profiles)
        logging.info("Scraping complete. Profiles saved to 'data/title_profile.csv'.")

def main():
   
    schedule.every().day.at("23:59").do(run_scraper)
    run_scraper()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

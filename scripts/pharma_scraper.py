import requests                           # Import modułu umożliwiającego wysyłanie zapytań HTTP
from bs4 import BeautifulSoup             # Import BeautifulSoup do parsowania kodu HTML
import csv                                # Import modułu do pracy z plikami CSV
import os                                 # Import modułu os do operacji na systemie plików
import time                               # Import modułu time, służącego do obsługi opóźnień i pomiaru czasu
import logging                            # Import modułu logging, który umożliwia logowanie komunikatów
import schedule                           # Import modułu schedule do planowania wykonywania zadań (pip install schedule)
import difflib                            # Import modułu difflib, służącego do dopasowań rozmytych (fuzzy matching)
import re                                 # Import modułu re do pracy z wyrażeniami regularnymi

# Konfiguracja logowania – ustawiamy poziom logowania i format komunikatów.
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

# Nagłówki zapytań HTTP – imitujemy przeglądarkę, aby uniknąć blokady.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def get_job_links(session):
    """
    Funkcja pobiera linki do ofert pracy z głównej strony.
    Korzysta z obiektu session do wysłania zapytania HTTP i parsuje otrzymany HTML.
    """
    try:
        response = session.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()  # Podnosi wyjątek, jeśli kod odpowiedzi HTTP wskazuje błąd.
    except requests.RequestException as e:
        logging.error(f"Error fetching main page: {e}")
        return []
    
    # Parsowanie HTML przy użyciu BeautifulSoup.
    soup = BeautifulSoup(response.text, "html.parser")
    job_links = []
    # Iteracja po wszystkich elementach <a> zawierających atrybut href.
    for job in soup.find_all("a", href=True):
        # Sprawdzamy, czy link zawiera fragment "job_display", co identyfikuje ofertę pracy.
        if "job_display" in job["href"]:
            job_url = f"https://www.europharmajobs.com/{job['href']}"
            if job_url not in job_links:
                job_links.append(job_url)
    return job_links

def filter_unwanted(text):
    """
    Funkcja usuwa niechciane linie tekstu.
    Przerywa dalsze przetwarzanie, gdy natrafi na frazy takie jak "apply now" lub "jobs by experience".
    """
    lines = text.splitlines()  # Podział tekstu na poszczególne linie.
    filtered = []
    for line in lines:
        low_line = line.strip().lower()  # Normalizacja – usunięcie zbędnych spacji i zamiana na małe litery.
        # Jeśli linia zawiera "apply now" lub "jobs by experience", przerywamy dalsze przetwarzanie.
        if "apply now" in low_line:
            break
        if "jobs by experience" in low_line:
            break
        filtered.append(line.strip())
    return "\n".join(filtered)

def scrape_job_profile(session, job_url):
    """
    Funkcja pobiera szczegóły oferty pracy (tytuł i opis) ze wskazanego linku.
    Wykorzystuje BeautifulSoup do parsowania strony oraz wyrażenia regularne i narzędzia fuzzy matching (difflib)
    do identyfikacji istotnych sekcji opisu oferty.
    """
    try:
        response = session.get(job_url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching job listing {job_url}: {e}")
        return {"Job Title": "N/A", "Profile": None}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Ekstrakcja tytułu oferty (element <h1>)
    job_title_element = soup.find("h1")
    job_title = job_title_element.text.strip() if job_title_element else "N/A"
    
    # Ograniczenie ekstrakcji do kontenera z opisem oferty (div o klasie "jobDisplay")
    container = soup.find("div", class_="jobDisplay")
    if not container:
        container = soup  # Jeśli kontener nie zostanie znaleziony, przeszukujemy całą stronę

    # Lista kluczowych fraz (nagłówków) wskazujących na sekcje z istotnymi informacjami
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
    # Normalizacja listy – usunięcie zbędnych spacji i zamiana na małe litery
    header_keywords = [k.strip().lower() for k in header_keywords]

    extracted_content = ""
    # Przeszukiwanie wszystkich elementów <h3> wewnątrz kontenera
    for header_element in container.find_all("h3"):
        header_text = header_element.get_text(separator=" ", strip=True).lower()
        # Pomijamy nagłówki stopki
        if "jobs by experience" in header_text:
            continue
        # Sprawdzamy, czy nagłówek zawiera bezpośrednio frazy z listy lub czy jest do nich podobny (fuzzy matching)
        if any(keyword in header_text for keyword in header_keywords) or \
           difflib.get_close_matches(header_text, header_keywords, n=1, cutoff=0.8):
            section_text = ""
            # Iterujemy po kolejnych elementach (sibling) po nagłówku
            for sibling in header_element.find_next_siblings():
                sibling_text = sibling.get_text(separator=" ", strip=True)
                # Kończymy, gdy natrafimy na frazę "apply now"
                if "apply now" in sibling_text.lower():
                    break
                section_text += sibling_text + "\n"
            extracted_content += section_text + "\n"
    
    # Filtrowanie niechcianych fragmentów tekstu
    profile = filter_unwanted(extracted_content.strip()) if extracted_content.strip() else None

    return {
        "Job Title": job_title,
        "Profile": profile
    }

def save_profiles_to_csv(job_data_list, filename="data/title_profile.csv"):
    """
    Zapisuje listę zebranych danych (tytuły ofert i ich opisy) do pliku CSV.
    Tworzy folder docelowy, jeśli nie istnieje.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Job Title", "Profile"])
        writer.writeheader()
        for job_data in job_data_list:
            writer.writerow(job_data)

def run_scraper():
    """
    Główna funkcja wykonująca cały proces:
      1. Pobiera linki do ofert pracy.
      2. Dla każdego linku pobiera szczegóły oferty (tytuł i opis).
      3. Zbiera wyniki i zapisuje je do pliku CSV.
    """
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
    """
    Główna funkcja uruchamiająca scraper:
      - Zaplanowane uruchamianie codziennie o 23:59.
      - Natychmiastowe uruchomienie scraper’a po starcie.
      - Pętla, która sprawdza i wykonuje zaplanowane zadania.
    """
    schedule.every().day.at("23:59").do(run_scraper)
    run_scraper()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import csv
import re
import os
import random

# -----------------------------
# CONFIG DYNAMIQUE
# -----------------------------
KEYWORDS_LIST = [
    "Data Analyst", "Data Scientist", "Data Engineer", "Business Intelligence",
    "Développeur Frontend", "Développeur Backend", "Développeur Fullstack",
    "Développeur Mobile", "DevOps", "Cloud", "Docker", "Kubernetes",
    "Cybersécurité", "Pentesting", "Administrateur Réseau", "Administrateur Systèmes",
    "Support IT", "Machine Learning", "Intelligence Artificielle", "Computer Vision",
    "DBA", "SQL", "NoSQL", "Chef de Projet IT", "Scrum", "Agile",
    "ERP", "SAP", "Odoo", "CRM", "Salesforce", "Informatique Général", "Ingénieur Informatique"
]
LOCATION = "Morocco"
FILENAME = "linkedin_jobs_dynamic_800.csv"
COLUMNS = ["title", "company", "location", "sector", "description", "required_skills", "required_education", "required_experience", "required_languages", "contract_type", "posted_date", "source"]

SKILLS_KEYWORDS = [
    "python", "sql", "aws", "docker", "kubernetes", "excel", "communication", 
    "javascript", "html", "css", "java", "php", "react", "angular", "node",
    "machine learning", "deep learning", "tableau", "power bi", "spark", "hadoop",
    "git", "linux", "c++", "c#", "scala", "mongodb", "postgresql", "mysql",
    "agile", "scrum", "project management"
]

# -----------------------------
# UTILS
# -----------------------------

def extract_skills(desc):
    if not desc: return "Non spécifiées"
    d = desc.lower()
    found = [s for s in SKILLS_KEYWORDS if s in d]
    return ", ".join(list(set(found))) if found else "Non spécifiées"

def extract_education(desc):
    if not desc: return "Non spécifié"
    d = desc.lower()
    patterns = ["bac+3", "bac+5", "master", "ingénieur", "licence", "doctorat", "phd", "bachelor"]
    found = [p for p in patterns if p in d]
    return ", ".join(list(set(found))) if found else "Non spécifié"

def extract_languages(desc):
    if not desc: return "Non spécifié"
    d = desc.lower()
    langs = ["français", "french", "anglais", "english", "arabe", "arabic", "espagnol", "spanish"]
    found = [l for l in langs if l in d]
    return ", ".join(list(set(found))) if found else "Non spécifié"

def load_processed_urls(filename):
    urls = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) > 11:
                    urls.add(row[11])  # The source URL is at index 11
    return urls

def init_csv(filename, columns):
    if not os.path.exists(filename):
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

# -----------------------------
# DRIVER CONFIG
# -----------------------------

def get_driver():
    print("  [DEBUG] Initialisation de Chrome...")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("window-size=1600,1200")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        # On essaie de démarrer le driver
        driver = webdriver.Chrome(options=chrome_options)
        print("  [DEBUG] Chrome démarré avec succès.")
        return driver
    except Exception as e:
        print(f"  [ERREUR] Impossible de lancer Chrome : {e}")
        print("  Vérifiez que Chrome est bien installé et à jour.")
        raise e

def close_login_modal(driver):
    try:
        close_selectors = [".modal__dismiss", ".modal-close-button", ".artdeco-modal__dismiss", "button[aria-label='Dismiss']"]
        for sel in close_selectors:
            btns = driver.find_elements(By.CSS_SELECTOR, sel)
            if btns and btns[0].is_displayed():
                btns[0].click()
                time.sleep(1)
    except: pass

# -----------------------------
# MAIN LOOP
# -----------------------------

processed_urls = load_processed_urls(FILENAME)
init_csv(FILENAME, COLUMNS)
print(f"Démarrage du scraping. {len(processed_urls)} offres déjà connues.")

while True:
    driver = None
    try:
        driver = get_driver()
        for keyword in KEYWORDS_LIST:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={LOCATION}&f_TPR=r86400" # Filtre : dernières 24h
            print(f"\n--- Recherche : '{keyword}' ---")
            driver.get(search_url)
            time.sleep(random.uniform(5, 8))
            close_login_modal(driver)

            # Étape 1 : Collecte des nouvelles URLs
            current_keyword_urls = []
            last_len = 0
            scroll_attempts = 0
            
            # On ne scrolle plus autant car on cherche juste les nouvelles offres
            for _ in range(5): 
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                cards = driver.find_elements(By.CSS_SELECTOR, ".base-card a, .job-search-card a, .base-search-card a")
                for a in cards:
                    try:
                        href = a.get_attribute("href")
                        if href and "/jobs/view/" in href:
                            clean_url = href.split("?")[0]
                            if clean_url not in processed_urls:
                                current_keyword_urls.append(clean_url)
                    except: continue
                
                current_keyword_urls = list(set(current_keyword_urls))
                if len(current_keyword_urls) == last_len:
                    scroll_attempts += 1
                    if scroll_attempts > 3: break
                else:
                    scroll_attempts = 0
                    last_len = len(current_keyword_urls)

            print(f"  {len(current_keyword_urls)} nouvelles offres trouvées pour '{keyword}'")

            # Étape 2 : Extraction
            for url in current_keyword_urls:
                try:
                    driver.get(url)
                    time.sleep(random.uniform(3, 6))
                    close_login_modal(driver)

                    title, company, location, date, sector, experience, contract = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
                    try:
                        title = driver.find_element(By.CSS_SELECTOR, "h1, .top-card-layout__title, .job-details-jobs-unified-top-card__job-title").text.strip()
                        company = driver.find_element(By.CSS_SELECTOR, ".topcard__org-name-link, .topcard__flavor--company, .job-details-jobs-unified-top-card__company-name").text.strip()
                    except: continue

                    try: location = driver.find_element(By.CSS_SELECTOR, ".topcard__flavor--bullet, .job-details-jobs-unified-top-card__bullet").text.strip()
                    except: pass
                    try: date = driver.find_element(By.CSS_SELECTOR, ".posted-time-ago__text, .job-details-jobs-unified-top-card__posted-date").text.strip()
                    except: pass

                    insights = driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-item, .job-details-jobs-unified-top-card__job-insight")
                    for item in insights:
                        text = item.text.lower()
                        val = item.text.split("\n")[-1]
                        if "niveau" in text or "seniority" in text: experience = val
                        elif "temps" in text or "emploi" in text or "employment" in text: contract = val
                        elif "secteur" in text or "industries" in text: sector = val

                    description_text = ""
                    try:
                        desc_elem = driver.find_element(By.CSS_SELECTOR, ".description__text, .jobs-description-content__text, .show-more-less-html__get-full-text")
                        description_text = desc_elem.text.replace("\n", " ").strip()
                    except: pass
                    
                    skills = extract_skills(description_text)
                    education = extract_education(description_text)
                    languages = extract_languages(description_text)

                    row = [title, company, location, sector, description_text, skills, education, experience, languages, contract, date, url]
                    with open(FILENAME, "a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.writer(f)
                        writer.writerow(row)
                    
                    processed_urls.add(url)
                    print(f"    ✓ {title} ({company})")
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    continue

    except Exception as e:
        print(f"Erreur critique dans la boucle : {e}")
    finally:
        if driver:
            driver.quit()
        
    delay = random.randint(300, 600) # Entre 5 et 10 minutes
    print(f"\nCycle terminé. Prochain passage dans {delay // 60} minutes...")
    time.sleep(delay)

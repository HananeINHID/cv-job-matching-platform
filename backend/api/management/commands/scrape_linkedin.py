import time
import random
import re
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from api.models import JobOffer

# CONFIG DYNAMIQUE (LOGIQUE ORIGINALE LinkedIn_scrap.py)
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

SKILLS_KEYWORDS = [
    "python", "sql", "aws", "docker", "kubernetes", "excel", "communication", 
    "javascript", "html", "css", "java", "php", "react", "angular", "node",
    "machine learning", "deep learning", "tableau", "power bi", "spark", "hadoop",
    "git", "linux", "c++", "c#", "scala", "mongodb", "postgresql", "mysql",
    "agile", "scrum", "project management"
]

class Command(BaseCommand):
    help = "Scraper LinkedIn synchronisé avec la logique d'extraction personnalisée de LinkedIn_scrap.py"

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Mot-clé spécifique à chercher')
        parser.add_argument('--limit', type=int, default=0, help='Nombre max d\'offres à scraper (0 = pas de limite)')
        parser.add_argument('--run-once', action='store_true', help='Forcer l\'arrêt après un seul passage')


    def extract_skills(self, desc):
        if not desc: return ""
        d = desc.lower()
        found = [s for s in SKILLS_KEYWORDS if s in d]
        return ", ".join(list(set(found))) if found else ""

    def extract_education(self, desc):
        if not desc: return ""
        d = desc.lower()
        patterns = ["bac+3", "bac+5", "master", "ingénieur", "licence", "doctorat", "phd", "bachelor"]
        found = [p for p in patterns if p in d]
        return ", ".join(list(set(found))) if found else ""

    def extract_languages(self, desc):
        if not desc: return ""
        d = desc.lower()
        langs = ["français", "french", "anglais", "english", "arabe", "arabic", "espagnol", "spanish"]
        found = [l for l in langs if l in d]
        return ", ".join(list(set(found))) if found else ""

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("window-size=1600,1200")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        # Options de stabilité et performance
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.page_load_strategy = 'eager'

        # chrome_options.add_argument("--headless") # Décommenter pour masquer la fenêtre
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver

    def close_login_modal(self, driver):
        try:
            close_selectors = [".modal__dismiss", ".modal-close-button", ".artdeco-modal__dismiss", "button[aria-label='Dismiss']"]
            for sel in close_selectors:
                btns = driver.find_elements(By.CSS_SELECTOR, sel)
                if btns and btns[0].is_displayed():
                    btns[0].click()
                    time.sleep(1)
        except: pass

    def handle(self, *args, **options):
        keyword_arg = options.get('keyword')
        limit = options.get('limit') or 0
        
        keywords_to_search = [keyword_arg] if keyword_arg else KEYWORDS_LIST
        
        self.stdout.write(self.style.SUCCESS(f"Démarrage du scraper LinkedIn (Mot-clé: {keyword_arg or 'TOUS'})"))
        
        # Si un mot-clé spécifique est fourni, ou si --run-once est passé, on ne boucle qu'une fois
        run_once = bool(keyword_arg) or options.get('run_once')
        
        while True:
            driver = None
            try:
                driver = self.get_driver()
                for keyword in keywords_to_search:
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={LOCATION}&f_TPR=r86400"
                    self.stdout.write(f"\n--- Recherche : '{keyword}' ---")
                    driver.get(search_url)
                    time.sleep(random.uniform(4, 6))
                    self.close_login_modal(driver)

                    # Collecte des URLs
                    cards = driver.find_elements(By.CSS_SELECTOR, ".base-card a, .job-search-card a, .base-search-card a")
                    current_keyword_urls = []
                    for a in cards:
                        try:
                            href = a.get_attribute("href")
                            if href and "/jobs/view/" in href:
                                clean_url = href.split("?")[0]
                                if not JobOffer.objects.filter(source_url=clean_url).exists():
                                    current_keyword_urls.append(clean_url)
                        except: continue
                    
                    current_keyword_urls = list(set(current_keyword_urls))
                    
                    # Appliquer la limite si définie
                    if limit > 0:
                        current_keyword_urls = current_keyword_urls[:limit]
                        
                    self.stdout.write(f"  {len(current_keyword_urls)} nouvelles offres à traiter.")

                    # Extraction et sauvegarde
                    for url in current_keyword_urls:
                        try:
                            driver.get(url)
                            time.sleep(random.uniform(2, 4))
                            self.close_login_modal(driver)

                            title = "N/A"
                            company = "N/A"
                            try:
                                title = driver.find_element(By.CSS_SELECTOR, "h1, .top-card-layout__title, .job-details-jobs-unified-top-card__job-title").text.strip()
                                company = driver.find_element(By.CSS_SELECTOR, ".topcard__org-name-link, .topcard__flavor--company, .job-details-jobs-unified-top-card__company-name").text.strip()
                            except: 
                                continue

                            description_text = ""
                            try:
                                desc_elem = driver.find_element(By.CSS_SELECTOR, ".description__text, .jobs-description-content__text, .show-more-less-html__get-full-text")
                                description_text = desc_elem.text.replace("\n", " ").strip()
                            except: pass
                            
                            skills = self.extract_skills(description_text)
                            education = self.extract_education(description_text)
                            languages = self.extract_languages(description_text)

                            JobOffer.objects.create(
                                title=title[:255],
                                company=company[:255],
                                description=description_text,
                                location=LOCATION,
                                required_skills=skills,
                                required_education=education,
                                required_languages=languages,
                                source="linkedin",
                                source_url=url,
                                is_active=True
                            )
                            self.stdout.write(self.style.SUCCESS(f"    ✓ {title} ({company}) sauvegardé."))
                            time.sleep(random.uniform(1, 2))

                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"    ✗ Erreur sur l'offre {url}: {e}"))
                            continue

                if driver: driver.quit()
                
                # Si on cherche un mot-clé précis, on arrête après un passage
                if run_once:
                    self.stdout.write(self.style.SUCCESS("Scraping terminé pour ce mot-clé."))
                    break
                    
                delay = random.randint(300, 600)
                self.stdout.write(self.style.SUCCESS(f"\nCycle terminé. Prochain passage dans {delay // 60} minutes..."))
                time.sleep(delay)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur critique dans la boucle : {e}"))
                if driver: driver.quit()
                if run_once: break
                time.sleep(60)

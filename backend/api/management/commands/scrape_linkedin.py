from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from api.models import JobOffer
import time
import random
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrape LinkedIn jobs and save them to the database'

    def handle(self, *args, **options):
        # CONFIG DYNAMIQUE
        KEYWORDS_LIST = [
            "Data Scientist", "Data Engineer", "Développeur React", 
            "DevOps", "Python", "Data Analyst", "Machine Learning"
        ]
        LOCATION = "Morocco"

        self.stdout.write(self.style.SUCCESS("Démarrage du scraper LinkedIn..."))
        
        driver = self.get_driver()
        try:
            while True:
                for keyword in KEYWORDS_LIST:
                    self.stdout.write(f"Recherche pour : {keyword}")
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={LOCATION}&f_TPR=r86400"
                    driver.get(search_url)
                    time.sleep(random.uniform(5, 8))

                    # Collecte des URLs
                    cards = driver.find_elements(By.CSS_SELECTOR, ".base-card a, .job-search-card a")
                    urls = []
                    for a in cards:
                        try:
                            href = a.get_attribute("href")
                            if href and "/jobs/view/" in href:
                                urls.append(href.split("?")[0])
                        except: continue
                    
                    urls = list(set(urls))
                    self.stdout.write(f"  {len(urls)} offres trouvées.")

                    for url in urls[:15]:
                        if JobOffer.objects.filter(source_url=url).exists():
                            continue
                        
                        try:
                            driver.get(url)
                            time.sleep(random.uniform(3, 5))
                            
                            # Extraction des données
                            title = driver.find_element(By.CSS_SELECTOR, "h1, .top-card-layout__title").text.strip()
                            company = driver.find_element(By.CSS_SELECTOR, ".topcard__org-name-link, .topcard__flavor--company").text.strip()
                            
                            description_text = ""
                            try:
                                desc_elem = driver.find_element(By.CSS_SELECTOR, ".description__text, .show-more-less-html__get-full-text")
                                description_text = desc_elem.text.strip()
                            except: pass

                            # Sauvegarde
                            JobOffer.objects.create(
                                title=title[:255],
                                company=company[:255],
                                description=description_text,
                                source="linkedin",
                                source_url=url,
                                is_active=True
                            )
                            self.stdout.write(self.style.SUCCESS(f"    ✓ Ajouté : {title}"))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"    × Erreur sur {url}"))
                            continue
                
                self.stdout.write("Cycle terminé. Pause de 10 minutes...")
                time.sleep(600)
        finally:
            driver.quit()

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("window-size=1200x800")
        return webdriver.Chrome(options=chrome_options)

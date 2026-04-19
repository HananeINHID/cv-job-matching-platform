import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import csv
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

class JobScraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        self.syn_exp = ["expérience", "pratique", "parcours", "ans", "année"]
        self.syn_comp = ["compétence", "capacité", "maîtrise", "technique", "outils"]
        self.syn_etudes = ["diplôme", "formation", "bac+", "licence", "master"]
        self.syn_langues = ["anglais", "français", "langues", "english", "french"]

    def clean_garbage(self, text):
        if not text: return "N/A"
        text = re.sub(r'\{[^}]*\}', '', text)
        garbage = ['background-color', 'padding', 'text-align', 'font-size', 'margin', '.text-block', 'color:']
        for word in garbage:
            text = text.replace(word, '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_soup(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=12)
            return BeautifulSoup(res.content, 'html.parser') if res.status_code == 200 else None
        except:
            return None

    def extract_smart_text(self, soup, keywords_list):
        if not soup: return ""
        for word in keywords_list:
            target = soup.find(string=re.compile(word, re.IGNORECASE))
            if target:
                parent = target.find_parent()
                return self.clean_garbage(parent.get_text(" ", strip=True))[:500]
        return ""

    def scrape_rekrute(self, kw, pages, today):
        results = []
        for p in range(1, pages + 1):
            url = f"https://www.rekrute.com/offres.html?s=1&p={p}&st=0&keyword={kw}"
            soup = self.get_soup(url)
            if not soup: continue
            for post in soup.find_all('li', class_='post-id'):
                link_tag = post.find('a', class_='titreJob')
                if not link_tag: continue
                detail = self.get_soup("https://www.rekrute.com" + link_tag['href'])
                results.append({
                    "title": link_tag.text.strip(),
                    "company": post.find('img', class_='logo')['title'] if post.find('img', class_='logo') else "N/A",
                    "location": post.find('span', class_='location').text.strip() if post.find('span', class_='location') else "Maroc",
                    "sector": kw,
                    "description": self.clean_garbage(detail.get_text())[:1500] if detail else "N/A",
                    "required_skills": self.extract_smart_text(detail, self.syn_comp),
                    "required_education": self.extract_smart_text(detail, self.syn_etudes),
                    "required_experience": self.extract_smart_text(detail, self.syn_exp),
                    "required_languages": self.extract_smart_text(detail, self.syn_langues),
                    "contract_type": post.find('span', class_='contract').text.strip() if post.find('span', class_='contract') else "N/A",
                    "posted_date": today
                })
        return results

    def scrape_emploima(self, kw, pages, today):
        results = []
        for p in range(0, pages):
            url = f"https://www.emploi.ma/recherche-jobs-maroc?search_api_views_fulltext={kw}&page={p}"
            soup = self.get_soup(url)
            if not soup: continue
            for item in soup.find_all('div', class_='job-description-wrapper'):
                link_tag = item.find('h5').find('a') if item.find('h5') else None
                if not link_tag: continue
                detail = self.get_soup("https://www.emploi.ma" + link_tag['href'])
                results.append({
                    "title": link_tag.text.strip(),
                    "company": item.find('div', class_='company-name').text.strip() if item.find('div', class_='company-name') else "N/A",
                    "location": item.find('div', class_='job-ad-item').text.strip() if item.find('div', class_='job-ad-item') else "Maroc",
                    "sector": kw,
                    "description": self.clean_garbage(detail.get_text())[:1500] if detail else "N/A",
                    "required_skills": self.extract_smart_text(detail, self.syn_comp),
                    "required_education": self.extract_smart_text(detail, self.syn_etudes),
                    "required_experience": self.extract_smart_text(detail, self.syn_exp),
                    "required_languages": self.extract_smart_text(detail, self.syn_langues),
                    "contract_type": "CDI",
                    "posted_date": today
                })
        return results

    def scrape_tanitjobs(self, kw, pages, today):
        results = []
        for p in range(1, pages + 1):
            url = f"https://www.tanitjobs.com/jobs/?searchId=1&keywords={kw}&page={p}"
            soup = self.get_soup(url)
            if not soup: continue
            for job in soup.find_all('div', class_='listing-item'):
                link = job.find('a', class_='title')
                if not link: continue
                detail = self.get_soup(link['href'])
                results.append({
                    "title": link.text.strip(),
                    "company": job.find('div', class_='company').text.strip() if job.find('div', class_='company') else "N/A",
                    "location": job.find('div', class_='location').text.strip() if job.find('div', class_='location') else "Maroc",
                    "sector": kw,
                    "description": self.clean_garbage(detail.get_text())[:1500] if detail else "N/A",
                    "required_skills": self.extract_smart_text(detail, self.syn_comp),
                    "required_education": self.extract_smart_text(detail, self.syn_etudes),
                    "required_experience": self.extract_smart_text(detail, self.syn_exp),
                    "required_languages": self.extract_smart_text(detail, self.syn_langues),
                    "contract_type": "N/A",
                    "posted_date": today
                })
        return results

    def scrape_optioncarriere(self, kw, pages, today):
        results = []
        for p in range(1, pages + 1):
            url = f"https://www.optioncarriere.ma/emploi-{kw.replace(' ', '-')}.html?p={p}"
            soup = self.get_soup(url)
            if not soup: continue
            for art in soup.find_all('article', class_='job'):
                link = art.find('a')
                if not link: continue
                results.append({
                    "title": link.text.strip(),
                    "company": art.find('p', class_='company').text.strip() if art.find('p', class_='company') else "N/A",
                    "location": art.find('ul', class_='location').text.strip() if art.find('ul', class_='location') else "Maroc",
                    "sector": kw,
                    "description": art.find('div', class_='desc').text.strip() if art.find('div', class_='desc') else "N/A",
                    "required_skills": "Non spécifié",
                    "required_education": "Non spécifié",
                    "required_experience": "Non spécifié",
                    "required_languages": "Non spécifié",
                    "contract_type": "N/A",
                    "posted_date": today
                })
        return results

    def scrape_marocannonces(self, kw, pages, today):
        results = []
        for p in range(1, pages + 1):
            url = f"https://www.marocannonces.com/maroc/offres-emploi-b309-p{p}.html?kw={kw}"
            soup = self.get_soup(url)
            if not soup: continue
            for item in soup.select('ul.list-annonces li.item'):
                link_tag = item.find('a')
                if not link_tag: continue
                detail = self.get_soup("https://www.marocannonces.com/" + link_tag['href'])
                results.append({
                    "title": link_tag.find('h3').text.strip() if link_tag.find('h3') else "N/A",
                    "company": "N/A",
                    "location": item.find('span', class_='location').text.strip() if item.find('span', class_='location') else "Maroc",
                    "sector": kw,
                    "description": self.clean_garbage(detail.get_text())[:1500] if detail else "N/A",
                    "required_skills": self.extract_smart_text(detail, self.syn_comp),
                    "required_education": self.extract_smart_text(detail, self.syn_etudes),
                    "required_experience": self.extract_smart_text(detail, self.syn_exp),
                    "required_languages": self.extract_smart_text(detail, self.syn_langues),
                    "contract_type": "N/A",
                    "posted_date": today
                })
        return results


def run_scraping_job():
    print(f"\n{'='*55}")
    print(f" SCRAPING DÉMARRÉ : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    scraper = JobScraper()

    domaines = [
        # Tech & Data
        "Python", "Data Science", "Machine Learning", "Intelligence Artificielle",
        "Big Data", "Développeur", "Java", "Fullstack", "Backend", "Frontend",
        "Cloud", "DevOps", "Cybersécurité", "Réseaux", "Systèmes", "Business Intelligence",
        # Industrie & Ingénierie
        "Ingénieur", "Automobile", "Aéronautique", "BTP", "Génie Civil",
        "Énergie", "Électricité", "Maintenance", "Qualité", "HSE", "Automatisme",
        # Finance & Gestion
        "Comptabilité", "Finance", "Audit", "Contrôle de gestion", "Banque",
        "Assurance", "Fiscalité", "Trésorerie",
        # Business & RH
        "Commercial", "Vente", "Marketing", "Communication", "E-commerce",
        "Ressources Humaines", "Recrutement", "Logistique", "Transport", "Achat",
        # Autres
        "Juridique", "Droit", "Santé", "Infirmier", "Pharmacie",
        "Tourisme", "Hôtellerie", "Restauration", "Enseignement"
    ]

    pages_par_site = 10
    nom_fichier = r"C:\PROJET_SCRAPING_IASD\dataset_dm.csv"
    today = datetime.now().strftime('%Y-%m-%d')
    nouvelles_donnees = []

    for d in domaines:
        print(f" Scraping : {d} ...")
        try:
            nouvelles_donnees.extend(scraper.scrape_rekrute(d, pages_par_site, today))
            nouvelles_donnees.extend(scraper.scrape_emploima(d, pages_par_site, today))
            nouvelles_donnees.extend(scraper.scrape_tanitjobs(d, pages_par_site, today))
            nouvelles_donnees.extend(scraper.scrape_optioncarriere(d, pages_par_site, today))
            nouvelles_donnees.extend(scraper.scrape_marocannonces(d, pages_par_site, today))
        except Exception as e:
            print(f"Erreur sur le domaine {d}: {e}")
        time.sleep(1)

    df_nouveau = pd.DataFrame(nouvelles_donnees)

    if os.path.exists(nom_fichier):
        print(f"\n Fusion avec {nom_fichier}...")
        df_ancien = pd.read_csv(nom_fichier, encoding='utf-8-sig')
        df_total = pd.concat([df_ancien, df_nouveau], ignore_index=True)
    else:
        print(f"\n Création du fichier {nom_fichier}.")
        df_total = df_nouveau

    initial_count = len(df_total)
    df_total = df_total.drop_duplicates(subset=['title', 'company', 'location'], keep='first')
    df_total.to_csv(nom_fichier, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)

    print(f"\n  Dataset final : {len(df_total)} offres")
    print(f"  Doublons supprimés : {initial_count - len(df_total)}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    scheduler.add_job(run_scraping_job, 'cron', hour=8,  minute=0, id='scraping_matin')
    scheduler.add_job(run_scraping_job, 'cron', hour=14, minute=0, id='scraping_aprem')

    scheduler.start()
    print(" Scheduler démarré - Scraping à 08:00 et 14:00 chaque jour")

    print(" Première exécution immédiate...\n")
    run_scraping_job()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\n Scheduler arrêté.")
# ══════════════════════════════════════════════════════════════════
#  emploima.py — Scraper Emploi.ma (autonome, Selenium Edge)
#
#  Prérequis : Microsoft Edge + msedgedriver dans le PATH
#
#  Usage :
#    python emploima.py "Data Analyst"   ← 1 domaine
#    python emploima.py                  ← tous les domaines
# ══════════════════════════════════════════════════════════════════

import requests
import re
import os
import csv
import json
import time
import random
import sys
from datetime import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════

OUTPUT_DIR    = r"C:\projet_dm"
MASTER_CSV    = os.path.join(OUTPUT_DIR, "offres_demploi.csv")
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")

COLONNES = [
    "title", "company", "location", "sector", "description",
    "required_skills", "required_education", "required_experience",
    "required_languages", "contract_type", "posted_date", "source"
]

DOMAINES = {
    "Data Analyst":              ["Data Analyst"],
    "Data Scientist":            ["Data Scientist"],
    "Data Engineer":             ["Data Engineer"],
    "Business Intelligence":     ["Business Intelligence", "Power BI"],
    "Développeur Frontend":      ["Développeur frontend", "React", "Angular", "Vue.js"],
    "Développeur Backend":       ["Développeur backend", "Python", "Java", "Node.js"],
    "Développeur Fullstack":     ["Développeur fullstack"],
    "Développeur Mobile":        ["Développeur mobile", "Flutter", "React Native"],
    "DevOps":                    ["DevOps", "CI/CD", "Jenkins"],
    "Cloud":                     ["Cloud", "AWS", "Azure", "Google Cloud"],
    "Docker / Kubernetes":       ["Docker", "Kubernetes"],
    "Cybersécurité":             ["Cybersécurité", "Sécurité informatique"],
    "Pentesting":                ["Penetration Testing", "OWASP"],
    "Administrateur Réseau":     ["Administrateur réseau"],
    "Administrateur Sys":        ["Administrateur systèmes", "Linux"],
    "Support IT":                ["Support informatique", "Technicien informatique"],
    "Machine Learning":          ["Machine Learning", "Deep Learning"],
    "Intelligence Artificielle": ["Intelligence artificielle", "NLP"],
    "Computer Vision":           ["Computer Vision", "TensorFlow", "PyTorch"],
    "DBA / SQL":                 ["SQL", "MySQL", "PostgreSQL", "Oracle"],
    "NoSQL":                     ["MongoDB", "Redis", "Cassandra"],
    "Chef de Projet IT":         ["Chef de projet IT"],
    "Scrum / Agile":             ["Scrum Master", "Product Owner", "Agile"],
    "ERP":                       ["SAP", "Odoo"],
    "CRM / Salesforce":          ["Salesforce", "CRM"],
    "Informatique Général":      ["Informatique"],
    "Ingénieur Informatique":    ["Ingénieur informatique"],
}

EMPLOIMA_OFFERS = 10

ENTREPRISES_GENERIQUES = [
    'multinational', 'construction btp', 'pj', 'société',
    'entreprise', 'prestation de service', 'confidentiel',
    'n/a', '', 'anonymous', 'anonyme'
]

# ══════════════════════════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════════════════════════

def clean(text, default="N/A"):
    if not text:
        return default
    return re.sub(r'\s+', ' ', str(text)).strip()

def extract_skills(text):
    if not text or text == "N/A":
        return "Non spécifié"
    skills_list = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
        'Kotlin', 'Swift', 'MATLAB', 'HTML', 'CSS', 'SASS', 'Bootstrap', 'Tailwind',
        'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Node.js', 'Express.js',
        'Django', 'Flask', 'Spring Boot', 'Laravel', 'Flutter', 'React Native',
        'Machine Learning', 'Deep Learning', 'Data Science', 'Data Analysis',
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch',
        'NLP', 'Computer Vision', 'Power BI', 'Tableau', 'QlikView',
        'Looker', 'Google Data Studio', 'SQL', 'MySQL', 'PostgreSQL', 'SQLite',
        'Oracle', 'MongoDB', 'Cassandra', 'Redis', 'AWS', 'Azure', 'Google Cloud',
        'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'GitLab CI', 'Terraform',
        'Ansible', 'Git', 'GitHub', 'GitLab', 'Jira', 'Confluence', 'Linux',
        'Bash', 'Shell', 'Cybersecurity', 'Penetration Testing', 'OWASP',
        'Network Security', 'SAP', 'Odoo', 'Salesforce', 'SEO', 'Analytics',
        'Google Ads', 'Facebook Ads', 'Excel', 'Word', 'PowerPoint', 'Sage',
        'WordPress', 'Photoshop', 'Illustrator', 'InDesign', 'Canva'
    ]
    found = []
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found.append(skill)
    return ', '.join(found[:8]) if found else "Non spécifié"

def extract_experience(text):
    if not text or text == "N/A":
        return "Non spécifié"
    for pattern in [
        r'(\d+)\s*(?:ans|années?)\s*(?:d\'expérience|d\'exp)',
        r'expérience\s*(?:de|d\'au moins)\s*(\d+)\s*(?:ans|années?)',
        r'(\d+)\s*\+\s*(?:ans|années?)',
        r'(débutant|junior|senior|confirmé|expert)',
    ]:
        m = re.search(pattern, text.lower())
        if m:
            return f"{m.group(1)} ans" if m.group(1).isdigit() else m.group(1).capitalize()
    return "Non spécifié"

def extract_education(text):
    if not text or text == "N/A":
        return "Non spécifié"
    for level, kws in [
        ('Doctorat', ['doctorat', 'phd']),
        ('Bac+5',    ['bac+5', 'bac plus 5', 'master', 'ingénieur', 'mastère']),
        ('Bac+4',    ['bac+4', 'bac plus 4', 'maîtrise']),
        ('Bac+3',    ['bac+3', 'bac plus 3', 'licence', 'bachelor']),
        ('Bac+2',    ['bac+2', 'bac plus 2', 'dut', 'bts', 'deug']),
        ('Bac',      ['niveau bac', 'baccalauréat']),
    ]:
        if any(k in text.lower() for k in kws):
            return level
    return "Non spécifié"

def extract_languages(text):
    if not text or text == "N/A":
        return "Non spécifié"
    langs = {
        'Français': ['français', 'french'],
        'Anglais':  ['anglais', 'english'],
        'Arabe':    ['arabe', 'arabic'],
        'Espagnol': ['espagnol', 'spanish'],
        'Allemand': ['allemand', 'german'],
    }
    found = []
    for lang, kws in langs.items():
        if any(k in text.lower() for k in kws):
            suffix = " (Courant)" if any(
                w in text.lower() for w in ['bilingue', 'courant']
            ) else ""
            found.append(lang + suffix)
    return ', '.join(found) if found else "Non spécifié"

def extract_contract(text):
    if not text:
        return "Non spécifié"
    t = text.lower()
    for c, kws in [
        ('CDI',        ['cdi']),
        ('CDD',        ['cdd']),
        ('Stage',      ['stage']),
        ('Freelance',  ['freelance', 'indépendant']),
        ('Alternance', ['alternance']),
        ('Intérim',    ['intérim', 'interim']),
    ]:
        if any(k in t for k in kws):
            return c
    return "Non spécifié"

# ══════════════════════════════════════════════════════════════════
#  PROGRESS
# ══════════════════════════════════════════════════════════════════

def load_progress(keywords):
    prog = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            prog = json.load(f)
    if "emploima" not in prog:
        prog["emploima"] = {}
    for kw in keywords:
        if kw not in prog["emploima"]:
            prog["emploima"][kw] = 0
    return prog

def save_progress(progress):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    print(f"  Progress sauvegardé : {PROGRESS_FILE}")

# ══════════════════════════════════════════════════════════════════
#  SAUVEGARDE DATASET
# ══════════════════════════════════════════════════════════════════

def save(all_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_new = pd.DataFrame(all_data, columns=COLONNES)
    df_new = df_new.drop_duplicates(subset=["title", "company"])
    if os.path.exists(MASTER_CSV):
        df_existing = pd.read_csv(MASTER_CSV, encoding='utf-8-sig')
        df_final    = pd.concat([df_existing, df_new], ignore_index=True)
        df_final    = df_final.drop_duplicates(subset=["title", "company"])
    else:
        df_final = df_new
    df_final.to_csv(MASTER_CSV, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    print(f"\n  Dataset mis à jour : {MASTER_CSV}")
    print(f"  Nouvelles offres   : {len(df_new)}")
    print(f"  Total dataset      : {len(df_final)}")
    return df_final

# ══════════════════════════════════════════════════════════════════
#  SCRAPER EMPLOI.MA (Selenium)
# ══════════════════════════════════════════════════════════════════

class EmploiMaScraper:

    def __init__(self):
        try:
            opts = EdgeOptions()
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--start-maximized")
            opts.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            )
            opts.add_argument("--lang=fr-MA,fr;q=0.9,en;q=0.8")
            opts.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            opts.add_experimental_option('useAutomationExtension', False)

            self.driver  = webdriver.Edge(options=opts)
            self.wait    = WebDriverWait(self.driver, 15)
            self.scraped = set()

            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins',   { get: () => [1,2,3,4,5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['fr-MA','fr','en'] });
                    window.chrome = { runtime: {} };
                """}
            )
            print("  [Emploi.ma] Selenium anti-détection activé ✓")

        except Exception as e:
            print(f"  [Emploi.ma] Selenium non disponible : {e}")
            self.driver = None

    def _delay(self, a=2.0, b=4.0):
        time.sleep(random.uniform(a, b))

    def _scroll(self):
        try:
            h = self.driver.execute_script("return document.body.scrollHeight")
            for i in range(random.randint(3, 5)):
                self.driver.execute_script(f"window.scrollTo(0,{int(h*(i+1)/5)});")
                time.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass

    def _get(self, *xpaths):
        for xp in xpaths:
            try:
                el = self.driver.find_element(By.XPATH, xp)
                t  = el.text.strip()
                if t:
                    return t
            except Exception:
                pass
        return "N/A"

    def _scrape_one(self, url):
        self.driver.get(url)
        self._delay(2, 5)
        self._scroll()
        self._delay(1, 2)

        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            body = ""
        try:
            h1 = self.driver.find_element(By.TAG_NAME, "h1").text
        except Exception:
            h1 = "N/A"

        title    = h1.split('-')[0].strip() if '-' in h1 else h1.strip()
        company  = self._get(
            "//div[contains(@class,'card-block-company')]//h3",
            "//span[contains(@class,'company')]"
        )
        location = self._get(
            "//li[contains(@class,'location-dot')]//span",
            "//li[contains(@class,'location-dot')]"
        )
        sector   = self._get(
            "//div[contains(@class,'field-name-field-entreprise-secteur')]"
            "//div[contains(@class,'field-item')]"
        )
        desc     = self._get(
            "//*[contains(@class,'job-description')]",
            "//h3[contains(text(),'Poste propos')]/following-sibling::*[1]"
        )
        skills   = self._get(
            "//*[contains(@class,'job-qualifications')]",
            "//h3[contains(text(),'Profil recherch')]/following-sibling::ul[1]"
        )
        educ = self._get("//li[contains(@class,'graduation-cap')]")
        exp  = self._get("//li[contains(@class,'chart')]")

        date = datetime.today().strftime('%Y-%m-%d')
        m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', body)
        if m:
            date = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

        print(f"    ✓ {title[:55]}")
        return {
            "title":               clean(title),
            "company":             clean(company),
            "location":            clean(location),
            "sector":              clean(sector),
            "description":         clean(desc)[:2000],
            "required_skills":     clean(skills) if skills != "N/A" else extract_skills(body),
            "required_education":  clean(educ)   if educ  != "N/A" else extract_education(body),
            "required_experience": clean(exp)     if exp   != "N/A" else extract_experience(body),
            "required_languages":  extract_languages(body),
            "contract_type":       extract_contract(body),
            "posted_date":         date,
            "source":              f"Emploi.ma | {url}",
        }

    def _get_links(self, keyword, page=0):
        url = (f"https://www.emploi.ma/recherche-jobs-maroc"
               f"?search_api_views_fulltext={requests.utils.quote(keyword)}")
        if page > 0:
            url += f"&page={page}"
        self.driver.get(url)
        self._delay(3, 6)
        self._scroll()
        self._delay(1, 2)
        return list(set([
            l.get_attribute('href')
            for l in self.driver.find_elements(
                By.XPATH, "//a[contains(@href,'offre-emploi-maroc')]"
            )
            if l.get_attribute('href')
        ]))

    def scrape(self, keyword, progress, max_offers=EMPLOIMA_OFFERS):
        if not self.driver:
            return []

        results    = []
        start_page = progress["emploima"].get(keyword, 0)
        page       = start_page
        count      = 0
        pages_done = 0
        MAX_PAGES  = 3

        print(f"\n  [Emploi.ma] '{keyword}' — page {start_page}")

        while count < max_offers and pages_done < MAX_PAGES:
            links     = self._get_links(keyword, page)
            new_links = [l for l in links if l not in self.scraped]

            if not new_links:
                page += 1
                pages_done += 1
                continue

            for link in new_links:
                if count >= max_offers:
                    break
                try:
                    result = self._scrape_one(link)
                    results.append(result)
                    self.scraped.add(link)
                    count += 1
                    self._delay(1, 3)
                except Exception as e:
                    print(f"    [ERREUR] {e}")

            page += 1
            pages_done += 1
            self._delay(2, 5)

        progress["emploima"][keyword] = page
        print(f"  [Emploi.ma] {len(results)} offres — prochain run page {page}")
        return results

    def quit(self):
        if self.driver:
            self.driver.quit()

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main(domaine_choisi=None):
    print(f"\n{'═'*62}")
    print(f"  EMPLOI.MA — {domaine_choisi or 'Tous les domaines'}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═'*62}")

    if domaine_choisi:
        if domaine_choisi not in DOMAINES:
            print(f"  [ERREUR] Domaine inconnu : '{domaine_choisi}'")
            return
        keywords = DOMAINES[domaine_choisi]
    else:
        keywords = list({kw for kws in DOMAINES.values() for kw in kws})

    progress = load_progress(keywords)
    scraper  = EmploiMaScraper()
    all_data = []

    try:
        for kw in keywords:
            data = scraper.scrape(kw, progress)
            all_data.extend(data)
            time.sleep(random.uniform(2, 4))
    except KeyboardInterrupt:
        print("\n  Arrêt manuel.")
    finally:
        scraper.quit()

    if all_data:
        save(all_data)
    else:
        print("\n  Aucune donnée collectée.")

    save_progress(progress)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(domaine_choisi=" ".join(sys.argv[1:]))
    else:
        main()

import requests
import re
import os
import csv
import json
import time
import random
import schedule
import sys
from datetime import datetime
from bs4 import BeautifulSoup
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

# ══════════════════════════════════════════════════════════════════
#  DOMAINES — divisés en keywords précis pour recherche rapide
#  Chaque domaine = 1 seul keyword envoyé au scraper
#  → évite de chercher 4-5 keywords inutilement
# ══════════════════════════════════════════════════════════════════

DOMAINES = {

    # ── Data & BI ──────────────────────────────────────────────────
    "Data Analyst":          ["Data Analyst"],
    "Data Scientist":        ["Data Scientist"],
    "Data Engineer":         ["Data Engineer"],
    "Business Intelligence": ["Business Intelligence", "Power BI"],

    # ── Développement web & mobile ─────────────────────────────────
    "Développeur Frontend":  ["Développeur frontend", "React", "Angular", "Vue.js"],
    "Développeur Backend":   ["Développeur backend", "Python", "Java", "Node.js"],
    "Développeur Fullstack": ["Développeur fullstack"],
    "Développeur Mobile":    ["Développeur mobile", "Flutter", "React Native"],

    # ── DevOps & Cloud ─────────────────────────────────────────────
    "DevOps":                ["DevOps", "CI/CD", "Jenkins"],
    "Cloud":                 ["Cloud", "AWS", "Azure", "Google Cloud"],
    "Docker / Kubernetes":   ["Docker", "Kubernetes"],

    # ── Cybersécurité ──────────────────────────────────────────────
    "Cybersécurité":         ["Cybersécurité", "Sécurité informatique"],
    "Pentesting":            ["Penetration Testing", "OWASP"],

    # ── Réseaux & Systèmes ─────────────────────────────────────────
    "Administrateur Réseau": ["Administrateur réseau"],
    "Administrateur Sys":    ["Administrateur systèmes", "Linux"],
    "Support IT":            ["Support informatique", "Technicien informatique"],

    # ── IA & ML ────────────────────────────────────────────────────
    "Machine Learning":      ["Machine Learning", "Deep Learning"],
    "Intelligence Artificielle": ["Intelligence artificielle", "NLP"],
    "Computer Vision":       ["Computer Vision", "TensorFlow", "PyTorch"],

    # ── Base de données ────────────────────────────────────────────
    "DBA / SQL":             ["SQL", "MySQL", "PostgreSQL", "Oracle"],
    "NoSQL":                 ["MongoDB", "Redis", "Cassandra"],

    # ── Gestion de projet IT ───────────────────────────────────────
    "Chef de Projet IT":     ["Chef de projet IT"],
    "Scrum / Agile":         ["Scrum Master", "Product Owner", "Agile"],

    # ── ERP & CRM ──────────────────────────────────────────────────
    "ERP":                   ["SAP", "Odoo"],
    "CRM / Salesforce":      ["Salesforce", "CRM"],

    # ── Général ────────────────────────────────────────────────────
    "Informatique Général":  ["Informatique"],
    "Ingénieur Informatique":["Ingénieur informatique"],
}

# Liste plate de tous les noms de domaines (pour le formulaire)
LISTE_DOMAINES = list(DOMAINES.keys())

# Pages par run (réduit à 1 pour être rapide quand lancé depuis formulaire)
REKRUTE_PAGES     = 1
EMPLOIMA_OFFERS   = 5
PAGES_PAR_KEYWORD = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

ENTREPRISES_GENERIQUES = [
    'multinational', 'construction btp', 'pj', 'société',
    'entreprise', 'prestation de service', 'confidentiel',
    'n/a', '', 'anonymous', 'anonyme'
]

# ══════════════════════════════════════════════════════════════════
#  PROGRESS
# ══════════════════════════════════════════════════════════════════

def load_progress(keywords):
    """Charge le progress.json. Initialise les nouveaux keywords à 0/1."""
    prog = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            prog = json.load(f)

    # S'assurer que toutes les sources existent
    for source in ["rekrute", "marocannonces", "emploima"]:
        if source not in prog:
            prog[source] = {}

    # Initialiser les nouveaux keywords
    for kw in keywords:
        if kw not in prog["rekrute"]:
            prog["rekrute"][kw] = 1
        if kw not in prog["marocannonces"]:
            prog["marocannonces"][kw] = 1
        if kw not in prog["emploima"]:
            prog["emploima"][kw] = 0

    return prog

def save_progress(progress):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    print(f"\n  Progress sauvegardé : {PROGRESS_FILE}")

# ══════════════════════════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════════════════════════

def clean(text, default="N/A"):
    if not text:
        return default
    return re.sub(r'\s+', ' ', str(text)).strip()

def clean_company(name, soup=None):
    name_clean = (name or "").strip()
    if name_clean.lower() in ENTREPRISES_GENERIQUES:
        if soup:
            boutique = soup.find('div', class_='boutique_cls')
            if boutique:
                h3 = boutique.find('h3')
                if h3:
                    real_name = clean(h3.text)
                    if real_name.lower() not in ENTREPRISES_GENERIQUES:
                        return real_name[:50]
        return "Confidentiel"
    return clean(name_clean)[:50]

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
#  SCRAPER 1 — REKRUTE.COM
# ══════════════════════════════════════════════════════════════════

class RekruteScraper:

    def scrape(self, keyword, progress, pages=REKRUTE_PAGES):
        results    = []
        today      = datetime.now().strftime('%Y-%m-%d')
        start_page = progress["rekrute"].get(keyword, 1)

        print(f"\n  [Rekrute] '{keyword}' — pages {start_page} → {start_page + pages - 1}")

        for page in range(start_page, start_page + pages):
            try:
                url  = f"https://www.rekrute.com/offres.html?keyword={requests.utils.quote(keyword)}&p={page}"
                resp = requests.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(resp.content, 'html.parser')
                cards = soup.find_all('li', class_='post-id')

                if not cards:
                    print(f"    Page {page} vide, arrêt.")
                    break

                for card in cards:
                    try:
                        title_el = card.find('a', class_='titreJob')
                        if not title_el:
                            continue
                        title = clean(title_el.text)
                        link  = "https://www.rekrute.com" + title_el['href']

                        det   = requests.get(link, headers=HEADERS, timeout=15)
                        dsoup = BeautifulSoup(det.content, 'html.parser')
                        full  = dsoup.get_text(" ", strip=True)

                        img = card.find('img')
                        if img and img.get('title'):
                            company = clean(
                                re.sub(r'(Nouveau|Urgent|★)\s*', '', img['title'])
                            )[:50]
                        else:
                            cel = card.find('div', class_='societe')
                            company = clean(cel.text)[:50] if cel else "Confidentiel"

                        loc_el   = card.find('span', class_='location')
                        location = clean(loc_el.text) if loc_el else "Maroc"

                        con_el   = card.find('span', class_='contract')
                        contract = extract_contract(con_el.text if con_el else "")

                        results.append({
                            "title":               title,
                            "company":             company,
                            "location":            location,
                            "sector":              keyword,
                            "description":         clean(full)[:2000],
                            "required_skills":     extract_skills(full),
                            "required_education":  extract_education(full),
                            "required_experience": extract_experience(full),
                            "required_languages":  extract_languages(full),
                            "contract_type":       contract,
                            "posted_date":         today,
                            "source":              f"Rekrute | {link}",
                        })
                        print(f"    ✓ {title[:55]}")
                        time.sleep(random.uniform(0.5, 1.0))

                    except Exception:
                        continue

                time.sleep(random.uniform(1.0, 2.0))

            except Exception as e:
                print(f"    [ERREUR page {page}] {e}")

        progress["rekrute"][keyword] = start_page + pages
        print(f"  [Rekrute] {len(results)} offres — prochain run page {start_page + pages}")
        return results

# ══════════════════════════════════════════════════════════════════
#  SCRAPER 2 — EMPLOI.MA (Selenium anti-détection)
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
            opts.add_experimental_option(
                'excludeSwitches', ['enable-automation', 'enable-logging']
            )
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
#  SCRAPER 3 — MAROCANNONCES.COM
# ══════════════════════════════════════════════════════════════════

class MarocAnnoncesScraper:

    BASE_URL   = "https://www.marocannonces.com"
    SEARCH_URL = "https://www.marocannonces.com/maroc"

    def _get_page(self, url, retries=3):
        for i in range(retries):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code == 200:
                    return BeautifulSoup(resp.content, 'html.parser')
            except Exception as e:
                print(f"    [RETRY {i+1}] {e}")
                time.sleep(2)
        return None

    def _get_listing_links(self, keyword, page=1):
        params = f"?kw={requests.utils.quote(keyword)}&cat=309"
        if page > 1:
            params += f"&page={page}"
        soup = self._get_page(self.SEARCH_URL + params)
        if not soup:
            return []
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/annonce/' in href and 'Offres-emploi' in href:
                full = href if href.startswith('http') else \
                       self.BASE_URL + '/' + href.lstrip('/')
                links.append(full)
        return list(set(links))

    def _scrape_detail(self, url):
        soup = self._get_page(url)
        if not soup:
            return None

        full_text = soup.get_text(" ", strip=True)

        h1    = soup.find('h1')
        title = clean(h1.text) if h1 else "N/A"
        title = re.sub(r'\s*/\s*bac\+?\d*\s*$', '', title, flags=re.IGNORECASE).strip()

        extra = {}
        ul = soup.find('ul', id='extraQuestionName')
        if ul:
            for li in ul.find_all('li'):
                text = li.get_text(" ", strip=True)
                for key in ['Domaine', 'Fonction', 'Contrat', 'Entreprise',
                            'Salaire', "Niveau d'études", 'Ville']:
                    if text.startswith(key + ' :') or text.startswith(key + ':'):
                        extra[key] = text.split(':', 1)[1].strip()

        company  = clean_company(extra.get('Entreprise', ''), soup=soup)
        location = extra.get('Ville', 'Maroc')
        if location == 'Maroc':
            city_link = soup.find('a', href=re.compile(r'-emploi$'))
            if city_link:
                location = clean(city_link.text)

        sector = extra.get('Domaine', extra.get('Fonction', 'N/A'))
        sector = sector[:50] if sector else 'N/A'

        desc_div = soup.find('div', class_='description')
        if desc_div:
            block = desc_div.find('div', class_='block')
            description = clean(
                block.get_text(" ", strip=True) if block
                else desc_div.get_text(" ", strip=True)
            )
        else:
            description = "N/A"

        education_raw = extra.get("Niveau d'études", "")
        education = extract_education(education_raw) if education_raw \
                    else extract_education(full_text)

        contract_raw = extra.get('Contrat', '')
        contract = extract_contract(contract_raw) if contract_raw \
                   else extract_contract(full_text)

        posted_date = datetime.now().strftime('%Y-%m-%d')
        ld = soup.find('script', type='application/ld+json')
        if ld:
            m = re.search(r'"datePosted"\s*:\s*"(\d{4}-\d{2}-\d{2})', ld.string or "")
            if m:
                posted_date = m.group(1)

        return {
            "title":               title,
            "company":             company,
            "location":            location,
            "sector":              sector,
            "description":         description[:2000],
            "required_skills":     extract_skills(description + " " + full_text),
            "required_education":  education,
            "required_experience": extract_experience(full_text),
            "required_languages":  extract_languages(full_text),
            "contract_type":       contract,
            "posted_date":         posted_date,
            "source":              f"MarocAnnonces | {url}",
        }

    def scrape(self, keyword, progress, pages=PAGES_PAR_KEYWORD):
        results    = []
        scraped    = set()
        start_page = progress["marocannonces"].get(keyword, 1)

        print(f"\n  [MarocAnnonces] '{keyword}' — pages {start_page} → {start_page + pages - 1}")

        for page in range(start_page, start_page + pages):
            links = self._get_listing_links(keyword, page)
            if not links:
                print(f"    Aucun lien page {page}, arrêt.")
                break

            new_links = [l for l in links if l not in scraped]
            print(f"    Page {page} → {len(new_links)} nouvelles offres")

            for link in new_links:
                try:
                    data = self._scrape_detail(link)
                    if data:
                        results.append(data)
                        scraped.add(link)
                        print(f"    ✓ {data['title'][:40]} | {data['company']}")
                    time.sleep(random.uniform(0.5, 1.0))
                except Exception as e:
                    print(f"    [ERREUR] {e}")

            time.sleep(random.uniform(1.0, 2.0))

        progress["marocannonces"][keyword] = start_page + pages
        print(f"  [MarocAnnonces] {len(results)} offres — prochain run page {start_page + pages}")
        return results

# ══════════════════════════════════════════════════════════════════
#  SCRAPER 4 — LINKEDIN.COM (Selenium Chrome, sans login)
# ══════════════════════════════════════════════════════════════════

class LinkedInScraper:
    """
    Scrape les offres LinkedIn publiques (sans connexion).

    Utilisation depuis job_search_views.py :
        scraper = LinkedInScraper()
        try:
            results = scraper.scrape(keyword, progress, max_offers=10, location="Morocco")
        finally:
            scraper.quit()
    """

    LOCATION_DEFAULT = "Morocco"

    SKILLS_KEYWORDS = [
        "python", "sql", "aws", "docker", "kubernetes", "excel",
        "javascript", "html", "css", "java", "php", "react", "angular",
        "node", "machine learning", "deep learning", "tableau", "power bi",
        "spark", "hadoop", "git", "linux", "c++", "c#", "scala",
        "mongodb", "postgresql", "mysql", "agile", "scrum",
        "project management", "tensorflow", "pytorch", "data science",
        "flask", "django", "spring", "kubernetes", "terraform",
    ]

    def __init__(self):
        try:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            opts = ChromeOptions()
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1600,1200")
            opts.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)

            self.driver  = webdriver.Chrome(options=opts)
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
            print("  [LinkedIn] Selenium Chrome anti-détection activé ✓")

        except Exception as e:
            print(f"  [LinkedIn] Selenium non disponible : {e}")
            self.driver = None

    # ── helpers ──────────────────────────────────────────────────────

    def _delay(self, a=2.0, b=4.0):
        time.sleep(random.uniform(a, b))

    def _close_modal(self):
        """Ferme la modale de connexion LinkedIn si elle apparaît."""
        try:
            selectors = [
                ".modal__dismiss",
                ".artdeco-modal__dismiss",
                "button[aria-label='Dismiss']",
                "button[aria-label='Fermer']",
            ]
            for sel in selectors:
                btns = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if btns and btns[0].is_displayed():
                    btns[0].click()
                    time.sleep(1)
                    return
        except Exception:
            pass

    def _extract_skills_from_text(self, text: str) -> str:
        if not text:
            return "Non spécifié"
        d = text.lower()
        found = list({s for s in self.SKILLS_KEYWORDS if s in d})
        return ", ".join(found) if found else "Non spécifié"

    # ── collect job URLs from the listing page ────────────────────────

    def _collect_urls(self, keyword: str, location: str, max_offers: int) -> list:
        """Scroll la page de résultats LinkedIn et collecte les URLs d'offres."""
        search_url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={requests.utils.quote(keyword)}"
            f"&location={requests.utils.quote(location)}"
        )
        self.driver.get(search_url)
        self._delay(4, 6)
        self._close_modal()

        urls      = []
        last_len  = 0
        no_change = 0

        while len(urls) < max_offers * 2:   # collect 2× to have margin after dedup
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._delay(2, 3)

            # Bouton "Afficher plus" / "See more jobs"
            try:
                more_btns = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "button.infinite-scroller__show-more-button"
                )
                if more_btns and more_btns[0].is_displayed():
                    more_btns[0].click()
                    self._delay(2, 3)
            except Exception:
                pass

            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".base-card a, .job-search-card a, .base-search-card a"
            )
            for a in cards:
                href = a.get_attribute("href") or ""
                if "/jobs/view/" in href:
                    clean_url = href.split("?")[0]
                    if clean_url not in self.scraped and clean_url not in urls:
                        urls.append(clean_url)

            if len(urls) == last_len:
                no_change += 1
                if no_change >= 8:
                    break
            else:
                no_change = 0
                last_len = len(urls)

        print(f"  [LinkedIn] {len(urls)} URLs collectées pour '{keyword}'")
        return urls[:max_offers]   # limit before extraction

    # ── extract one job detail page ────────────────────────────────────

    def _scrape_one(self, url: str) -> dict | None:
        """Extrait les données d'une page de détail LinkedIn."""
        try:
            self.driver.get(url)
            self._delay(2, 4)
            self._close_modal()

            title   = "N/A"
            company = "N/A"
            location_val = "N/A"
            date    = datetime.now().strftime('%Y-%m-%d')
            sector  = "N/A"
            experience = "Non spécifié"
            contract   = "Non spécifié"

            # ── titre
            for sel in ["h1", ".top-card-layout__title",
                        ".job-details-jobs-unified-top-card__job-title"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    title = els[0].text.strip()
                    if title:
                        break

            # ── entreprise
            for sel in [".topcard__org-name-link", ".topcard__flavor--company",
                        ".job-details-jobs-unified-top-card__company-name"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    company = els[0].text.strip()
                    if company:
                        break

            if title == "N/A" or company == "N/A":
                return None   # page invalide

            # ── localisation
            for sel in [".topcard__flavor--bullet",
                        ".job-details-jobs-unified-top-card__bullet"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    location_val = els[0].text.strip()
                    break

            # ── date
            for sel in [".posted-time-ago__text",
                        ".job-details-jobs-unified-top-card__posted-date"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    date = els[0].text.strip() or date
                    break

            # ── insights (secteur, contrat, expérience)
            insights = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".description__job-criteria-item, "
                ".job-details-jobs-unified-top-card__job-insight"
            )
            for item in insights:
                text = item.text.lower()
                val  = item.text.split("\n")[-1].strip()
                if "niveau" in text or "seniority" in text:
                    experience = val
                elif "temps" in text or "emploi" in text or "employment" in text:
                    contract = extract_contract(val + " " + text)
                elif "secteur" in text or "industries" in text:
                    sector = val

            # ── description
            description = ""
            for sel in [".description__text",
                        ".jobs-description-content__text",
                        ".show-more-less-html__markup"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    description = els[0].text.replace("\n", " ").strip()
                    if description:
                        break

            skills    = self._extract_skills_from_text(description)
            education = extract_education(description)
            languages = extract_languages(description)
            if contract == "Non spécifié":
                contract = extract_contract(description)
            if experience == "Non spécifié":
                experience = extract_experience(description)

            print(f"    ✓ {title[:55]}")
            return {
                "title":               clean(title)[:255],
                "company":             clean(company)[:255],
                "location":            clean(location_val)[:255],
                "sector":              clean(sector)[:255],
                "description":         description[:2000],
                "required_skills":     skills,
                "required_education":  education,
                "required_experience": experience[:100],
                "required_languages":  languages,
                "contract_type":       contract[:100],
                "posted_date":         datetime.now().strftime('%Y-%m-%d'),
                "source":              f"LinkedIn | {url}",
            }

        except Exception as e:
            print(f"    [ERREUR LinkedIn] {e}")
            return None

    # ── public API ─────────────────────────────────────────────────────

    def scrape(self, keyword: str, progress: dict,
               max_offers: int = 10, location: str = LOCATION_DEFAULT) -> list:
        """
        Scrape LinkedIn pour `keyword` dans `location`.
        `progress` n'est pas utilisé (LinkedIn ne pagine pas de façon persistante)
        mais est conservé pour la cohérence de l'interface.
        """
        if not self.driver:
            return []

        results = []
        print(f"\n  [LinkedIn] '{keyword}' — {location} (max {max_offers})")

        urls = self._collect_urls(keyword, location, max_offers)
        for url in urls:
            if len(results) >= max_offers:
                break
            if url in self.scraped:
                continue
            data = self._scrape_one(url)
            if data:
                results.append(data)
                self.scraped.add(url)
            self._delay(1.5, 3.0)

        print(f"  [LinkedIn] {len(results)} offres extraites pour '{keyword}'")
        return results

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
#  SAUVEGARDE
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
#  RAPPORT
# ══════════════════════════════════════════════════════════════════

def report(df, domaine=None):
    print(f"\n{'═'*62}")
    print(f"  RAPPORT{'  — Domaine : ' + domaine if domaine else ''}")
    print(f"{'═'*62}")
    print(f"  Total offres dans offres_demploi.csv : {len(df)}")
    if 'source' in df.columns:
        for src in ['Rekrute', 'Emploi.ma', 'MarocAnnonces']:
            n = df['source'].str.contains(src, na=False).sum()
            print(f"    {src:<20} : {n} offres")
    print(f"{'═'*62}\n")

# ══════════════════════════════════════════════════════════════════
#  MAIN — 2 modes :
#    1. python emploi.py "Data Analyst"    ← depuis le formulaire
#    2. python emploi.py                   ← scheduler (tous domaines)
# ══════════════════════════════════════════════════════════════════

def main(domaine_choisi=None):
    print(f"\n{'═'*62}")
    if domaine_choisi:
        print(f"  SCRAPING RAPIDE — Domaine : {domaine_choisi}")
        print(f"  Lancé depuis formulaire — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"  SCRAPING COMPLET — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═'*62}")

    # ── Déterminer les keywords à scraper ─────────────────────────
    if domaine_choisi:
        # Mode formulaire : 1 seul domaine choisi par l'utilisateur
        if domaine_choisi not in DOMAINES:
            print(f"  [ERREUR] Domaine inconnu : {domaine_choisi}")
            print(f"  Domaines disponibles : {', '.join(LISTE_DOMAINES)}")
            return
        keywords = DOMAINES[domaine_choisi]
        print(f"  Keywords : {keywords}")
    else:
        # Mode scheduler : tous les domaines
        keywords = list({kw for kws in DOMAINES.values() for kw in kws})

    # ── Charger le progress ───────────────────────────────────────
    progress = load_progress(keywords)
    print(f"\n  Pages de départ chargées depuis progress.json")

    all_data = []

    # ── SOURCE 1 : REKRUTE ────────────────────────────────────────
    print("\n" + "─"*62)
    print("  SOURCE 1 : REKRUTE.COM")
    print("─"*62)
    rekrute = RekruteScraper()
    for kw in keywords:
        data = rekrute.scrape(kw, progress, pages=REKRUTE_PAGES)
        all_data.extend(data)
        time.sleep(random.uniform(1, 2))

    # ── SOURCE 2 : EMPLOI.MA ──────────────────────────────────────
    print("\n" + "─"*62)
    print("  SOURCE 2 : EMPLOI.MA")
    print("─"*62)
    emploima = EmploiMaScraper()
    try:
        for kw in keywords:
            data = emploima.scrape(kw, progress, max_offers=EMPLOIMA_OFFERS)
            all_data.extend(data)
            time.sleep(random.uniform(2, 4))
    except KeyboardInterrupt:
        print("\n  Arrêt manuel")
    finally:
        emploima.quit()

    # ── SOURCE 3 : MAROCANNONCES ──────────────────────────────────
    print("\n" + "─"*62)
    print("  SOURCE 3 : MAROCANNONCES.COM")
    print("─"*62)
    marocannonces = MarocAnnoncesScraper()
    for kw in keywords:
        data = marocannonces.scrape(kw, progress, pages=PAGES_PAR_KEYWORD)
        all_data.extend(data)
        time.sleep(random.uniform(1, 2))

    # ── Sauvegarde ────────────────────────────────────────────────
    if all_data:
        df_final = save(all_data)
        report(df_final, domaine=domaine_choisi)
    else:
        print("\n  Aucune donnée collectée.")

    save_progress(progress)

# ══════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
#
#  Depuis formulaire backend :
#    python emploi.py "Data Analyst"
#
#  Depuis Task Scheduler Windows (tous les domaines) :
#    python emploi.py
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # ── Mode formulaire : domaine passé en argument ────────────
        domaine = " ".join(sys.argv[1:])
        print(f"\n  Domaine reçu depuis formulaire : '{domaine}'")
        main(domaine_choisi=domaine)
    else:
        # ── Mode scheduler : tous les domaines, 08h00 et 18h00 ────
        schedule.every().day.at("16:03").do(main)
        schedule.every().day.at("20:00").do(main)
        print("  Scheduler démarré — 16h03 et 20h00")
        print(f"  Dataset : {MASTER_CSV}")
        while True:
            schedule.run_pending()
            time.sleep(60)
# ══════════════════════════════════════════════════════════════════
#  marocannonces.py — Scraper MarocAnnonces.com (autonome)
#
#  Usage :
#    python marocannonces.py "Data Analyst"   ← 1 domaine
#    python marocannonces.py                  ← tous les domaines
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
from bs4 import BeautifulSoup
import pandas as pd

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

PAGES_PAR_KEYWORD = 2

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
#  PROGRESS
# ══════════════════════════════════════════════════════════════════

def load_progress(keywords):
    prog = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            prog = json.load(f)
    if "marocannonces" not in prog:
        prog["marocannonces"] = {}
    for kw in keywords:
        if kw not in prog["marocannonces"]:
            prog["marocannonces"][kw] = 1
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
#  SCRAPER MAROCANNONCES
# ══════════════════════════════════════════════════════════════════

BASE_URL   = "https://www.marocannonces.com"
SEARCH_URL = "https://www.marocannonces.com/maroc"

def get_page(url, retries=3):
    for i in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return BeautifulSoup(resp.content, 'html.parser')
        except Exception as e:
            print(f"    [RETRY {i+1}] {e}")
            time.sleep(2)
    return None

def get_listing_links(keyword, page=1):
    params = f"?kw={requests.utils.quote(keyword)}&cat=309"
    if page > 1:
        params += f"&page={page}"
    soup = get_page(SEARCH_URL + params)
    if not soup:
        return []
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/annonce/' in href and 'Offres-emploi' in href:
            full = href if href.startswith('http') else BASE_URL + '/' + href.lstrip('/')
            links.append(full)
    return list(set(links))

def scrape_detail(url):
    soup = get_page(url)
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
    education = extract_education(education_raw) if education_raw else extract_education(full_text)

    contract_raw = extra.get('Contrat', '')
    contract = extract_contract(contract_raw) if contract_raw else extract_contract(full_text)

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

def scrape_marocannonces(keyword, progress, pages=PAGES_PAR_KEYWORD):
    results    = []
    scraped    = set()
    start_page = progress["marocannonces"].get(keyword, 1)

    print(f"\n  [MarocAnnonces] '{keyword}' — pages {start_page} → {start_page + pages - 1}")

    for page in range(start_page, start_page + pages):
        links = get_listing_links(keyword, page)
        if not links:
            print(f"    Aucun lien page {page}, arrêt.")
            break

        new_links = [l for l in links if l not in scraped]
        print(f"    Page {page} → {len(new_links)} nouvelles offres")

        for link in new_links:
            try:
                data = scrape_detail(link)
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
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main(domaine_choisi=None):
    print(f"\n{'═'*62}")
    print(f"  MAROCANNONCES — {domaine_choisi or 'Tous les domaines'}")
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
    all_data = []

    for kw in keywords:
        data = scrape_marocannonces(kw, progress)
        all_data.extend(data)
        time.sleep(random.uniform(1, 2))

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

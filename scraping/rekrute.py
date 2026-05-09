# ══════════════════════════════════════════════════════════════════
#  rekrute.py — Scraper Rekrute.com (autonome)
#
#  Usage :
#    python rekrute.py "Data Analyst"   ← 1 domaine
#    python rekrute.py                  ← tous les domaines
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

REKRUTE_PAGES = 2

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
    if "rekrute" not in prog:
        prog["rekrute"] = {}
    for kw in keywords:
        if kw not in prog["rekrute"]:
            prog["rekrute"][kw] = 1
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
#  SCRAPER REKRUTE
# ══════════════════════════════════════════════════════════════════

def scrape_rekrute(keyword, progress, pages=REKRUTE_PAGES):
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
                        company = clean(re.sub(r'(Nouveau|Urgent|★)\s*', '', img['title']))[:50]
                    else:
                        cel     = card.find('div', class_='societe')
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
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main(domaine_choisi=None):
    print(f"\n{'═'*62}")
    print(f"  REKRUTE — {domaine_choisi or 'Tous les domaines'}")
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
        data = scrape_rekrute(kw, progress)
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

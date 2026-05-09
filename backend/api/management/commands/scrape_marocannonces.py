import time
import random
import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from api.models import JobOffer

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════

KEYWORDS_LIST = [
    "Data Analyst", "Data Scientist", "Data Engineer", "Business Intelligence",
    "Développeur Frontend", "Développeur Backend", "Développeur Fullstack",
    "Développeur Mobile", "DevOps", "Cloud", "Docker", "Kubernetes",
    "Cybersécurité", "Pentesting", "Administrateur Réseau", "Administrateur Systèmes",
    "Support IT", "Machine Learning", "Intelligence Artificielle", "Computer Vision",
    "DBA", "SQL", "NoSQL", "Chef de Projet IT", "Scrum", "Agile",
    "ERP", "SAP", "Odoo", "CRM", "Salesforce", "Informatique Général", "Ingénieur Informatique"
]

PAGES_PAR_KEYWORD = 2

BASE_URL   = "https://www.marocannonces.com"
SEARCH_URL = "https://www.marocannonces.com/maroc"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

ENTREPRISES_GENERIQUES = [
    'multinational', 'construction btp', 'pj', 'société', 'entreprise',
    'prestation de service', 'confidentiel', 'n/a', '', 'anonymous', 'anonyme'
]

SKILLS_KEYWORDS = [
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

# ══════════════════════════════════════════════════════════════════
#  COMMANDE DJANGO
# ══════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = "Scraper MarocAnnonces.com — stockage direct dans la base de données"

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Mot-clé spécifique à chercher')
        parser.add_argument('--pages',   type=int, default=PAGES_PAR_KEYWORD, help='Nombre de pages par keyword')
        parser.add_argument('--limit',   type=int, default=0, help='Nombre max d\'offres (0 = pas de limite)')

    # ── Utilitaires d'extraction ──────────────────────────────────

    def clean(self, text, default="N/A"):
        if not text:
            return default
        return re.sub(r'\s+', ' ', str(text)).strip()

    def clean_company(self, name, soup=None):
        name_clean = (name or "").strip()
        if name_clean.lower() in ENTREPRISES_GENERIQUES:
            if soup:
                boutique = soup.find('div', class_='boutique_cls')
                if boutique:
                    h3 = boutique.find('h3')
                    if h3:
                        real_name = self.clean(h3.text)
                        if real_name.lower() not in ENTREPRISES_GENERIQUES:
                            return real_name[:255]
            return "Confidentiel"
        return self.clean(name_clean)[:255]

    def extract_skills(self, text):
        if not text:
            return ""
        found = []
        for skill in SKILLS_KEYWORDS:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found.append(skill)
        return ', '.join(found[:8]) if found else ""

    def extract_education(self, text):
        if not text:
            return ""
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
        return ""

    def extract_experience(self, text):
        if not text:
            return ""
        for pattern in [
            r'(\d+)\s*(?:ans|années?)\s*(?:d\'expérience|d\'exp)',
            r'expérience\s*(?:de|d\'au moins)\s*(\d+)\s*(?:ans|années?)',
            r'(\d+)\s*\+\s*(?:ans|années?)',
            r'(débutant|junior|senior|confirmé|expert)',
        ]:
            m = re.search(pattern, text.lower())
            if m:
                return f"{m.group(1)} ans" if m.group(1).isdigit() else m.group(1).capitalize()
        return ""

    def extract_languages(self, text):
        if not text:
            return ""
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
                found.append(lang)
        return ', '.join(found) if found else ""

    def extract_contract(self, text):
        if not text:
            return ""
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
        return ""

    # ── Réseau ────────────────────────────────────────────────────

    def get_page(self, url, retries=3):
        for i in range(retries):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code == 200:
                    return BeautifulSoup(resp.content, 'html.parser')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    [RETRY {i+1}] {e}"))
                time.sleep(2)
        return None

    def get_listing_links(self, keyword, page=1):
        params = f"?kw={requests.utils.quote(keyword)}&cat=309"
        if page > 1:
            params += f"&page={page}"
        soup = self.get_page(SEARCH_URL + params)
        if not soup:
            return []
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/annonce/' in href and 'Offres-emploi' in href:
                full = href if href.startswith('http') else BASE_URL + '/' + href.lstrip('/')
                links.append(full)
        return list(set(links))

    # ── Scraping d'une offre ──────────────────────────────────────

    def scrape_detail(self, url):
        soup = self.get_page(url)
        if not soup:
            return False

        full_text = soup.get_text(" ", strip=True)

        h1    = soup.find('h1')
        title = self.clean(h1.text) if h1 else "N/A"
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

        company  = self.clean_company(extra.get('Entreprise', ''), soup=soup)
        location = extra.get('Ville', 'Maroc')
        if location == 'Maroc':
            city_link = soup.find('a', href=re.compile(r'-emploi$'))
            if city_link:
                location = self.clean(city_link.text)

        desc_div = soup.find('div', class_='description')
        if desc_div:
            block = desc_div.find('div', class_='block')
            description = self.clean(
                block.get_text(" ", strip=True) if block
                else desc_div.get_text(" ", strip=True)
            )
        else:
            description = ""

        education_raw = extra.get("Niveau d'études", "")
        education = self.extract_education(education_raw) if education_raw \
                    else self.extract_education(full_text)

        contract_raw = extra.get('Contrat', '')
        contract = self.extract_contract(contract_raw) if contract_raw \
                   else self.extract_contract(full_text)

        JobOffer.objects.create(
            title=title[:255],
            company=company,
            location=location,
            description=description[:5000],
            required_skills=self.extract_skills(description + " " + full_text),
            required_education=education,
            required_experience=self.extract_experience(full_text),
            required_languages=self.extract_languages(full_text),
            contract_type=contract,
            source="marocannonces",
            source_url=url,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f"    ✓ {title[:60]} ({company[:40]}) sauvegardé."))
        return True

    # ── Handle ────────────────────────────────────────────────────

    def handle(self, *args, **options):
        keyword_arg = options.get('keyword')
        pages       = options.get('pages') or PAGES_PAR_KEYWORD
        limit       = options.get('limit') or 0

        keywords_to_search = [keyword_arg] if keyword_arg else KEYWORDS_LIST
        run_once           = bool(keyword_arg)

        self.stdout.write(self.style.SUCCESS(
            f"Démarrage du scraper MarocAnnonces (Mot-clé: {keyword_arg or 'TOUS'})"
        ))

        while True:
            total = 0
            try:
                for keyword in keywords_to_search:
                    self.stdout.write(f"\n--- Recherche : '{keyword}' ---")
                    scraped = set()
                    count   = 0

                    for page in range(1, pages + 1):
                        if limit > 0 and count >= limit:
                            break

                        links = self.get_listing_links(keyword, page)
                        if not links:
                            self.stdout.write(f"    Page {page} vide, arrêt.")
                            break

                        new_links = [
                            l for l in links
                            if l not in scraped
                            and not JobOffer.objects.filter(source_url=l).exists()
                        ]
                        self.stdout.write(f"    Page {page} → {len(new_links)} nouvelles offres")

                        for link in new_links:
                            if limit > 0 and count >= limit:
                                break
                            try:
                                ok = self.scrape_detail(link)
                                if ok:
                                    scraped.add(link)
                                    count += 1
                                time.sleep(random.uniform(0.5, 1.0))
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"    ✗ Erreur : {e}"))

                        time.sleep(random.uniform(1.0, 2.0))

                    total += count
                    self.stdout.write(f"  '{keyword}' → {count} offres sauvegardées.")
                    time.sleep(random.uniform(1, 2))

                self.stdout.write(self.style.SUCCESS(
                    f"\nCycle terminé — {total} offres sauvegardées en base."
                ))

                if run_once:
                    break

                delay = random.randint(300, 600)
                self.stdout.write(self.style.SUCCESS(
                    f"Prochain passage dans {delay // 60} minutes..."
                ))
                time.sleep(delay)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur critique : {e}"))
                if run_once:
                    break
                time.sleep(60)

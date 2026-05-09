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

REKRUTE_PAGES = 2

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
    help = "Scraper Rekrute.com — stockage direct dans la base de données"

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Mot-clé spécifique à chercher')
        parser.add_argument('--pages',   type=int, default=REKRUTE_PAGES, help='Nombre de pages par keyword')
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

    # ── Scraping ──────────────────────────────────────────────────

    def scrape_keyword(self, keyword, pages, limit):
        count = 0
        for page in range(1, pages + 1):
            try:
                url  = f"https://www.rekrute.com/offres.html?keyword={requests.utils.quote(keyword)}&p={page}"
                resp = requests.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(resp.content, 'html.parser')
                cards = soup.find_all('li', class_='post-id')

                if not cards:
                    self.stdout.write(f"    Page {page} vide, arrêt.")
                    break

                for card in cards:
                    if limit > 0 and count >= limit:
                        return count
                    try:
                        title_el = card.find('a', class_='titreJob')
                        if not title_el:
                            continue

                        title     = self.clean(title_el.text)
                        offer_url = "https://www.rekrute.com" + title_el['href']

                        # Vérifier doublon
                        if JobOffer.objects.filter(source_url=offer_url).exists():
                            self.stdout.write(f"    [SKIP] Déjà en base : {title[:50]}")
                            continue

                        # Page détail
                        det   = requests.get(offer_url, headers=HEADERS, timeout=15)
                        dsoup = BeautifulSoup(det.content, 'html.parser')
                        full  = dsoup.get_text(" ", strip=True)

                        # Entreprise
                        img = card.find('img')
                        if img and img.get('title'):
                            company = self.clean(
                                re.sub(r'(Nouveau|Urgent|★)\s*', '', img['title'])
                            )[:255]
                        else:
                            cel     = card.find('div', class_='societe')
                            company = self.clean(cel.text)[:255] if cel else "Confidentiel"

                        loc_el   = card.find('span', class_='location')
                        location = self.clean(loc_el.text) if loc_el else "Maroc"

                        con_el   = card.find('span', class_='contract')
                        contract = self.extract_contract(con_el.text if con_el else "")

                        JobOffer.objects.create(
                            title=title[:255],
                            company=company,
                            location=location,
                            description=self.clean(full)[:5000],
                            required_skills=self.extract_skills(full),
                            required_education=self.extract_education(full),
                            required_experience=self.extract_experience(full),
                            required_languages=self.extract_languages(full),
                            contract_type=contract,
                            source="rekrute",
                            source_url=offer_url,
                            is_active=True,
                        )
                        count += 1
                        self.stdout.write(self.style.SUCCESS(f"    ✓ {title[:60]} ({company[:40]}) sauvegardé."))
                        time.sleep(random.uniform(0.5, 1.0))

                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"    ✗ Erreur offre : {e}"))
                        continue

                time.sleep(random.uniform(1.0, 2.0))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    [ERREUR page {page}] {e}"))

        return count

    # ── Handle ────────────────────────────────────────────────────

    def handle(self, *args, **options):
        keyword_arg = options.get('keyword')
        pages       = options.get('pages') or REKRUTE_PAGES
        limit       = options.get('limit') or 0

        keywords_to_search = [keyword_arg] if keyword_arg else KEYWORDS_LIST
        run_once           = bool(keyword_arg)

        self.stdout.write(self.style.SUCCESS(
            f"Démarrage du scraper Rekrute (Mot-clé: {keyword_arg or 'TOUS'})"
        ))

        while True:
            total = 0
            try:
                for keyword in keywords_to_search:
                    self.stdout.write(f"\n--- Recherche : '{keyword}' ---")
                    n = self.scrape_keyword(keyword, pages, limit)
                    total += n
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

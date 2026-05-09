import time
import random
import re
import requests
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

EMPLOIMA_OFFERS = 10

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
    help = "Scraper Emploi.ma (Selenium Edge) — stockage direct dans la base de données"

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, help='Mot-clé spécifique à chercher')
        parser.add_argument('--limit',   type=int, default=EMPLOIMA_OFFERS, help='Nombre max d\'offres par keyword')

    # ── Utilitaires d'extraction ──────────────────────────────────

    def clean(self, text, default="N/A"):
        if not text:
            return default
        return re.sub(r'\s+', ' ', str(text)).strip()

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

    # ── Driver Selenium ───────────────────────────────────────────

    def get_driver(self):
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

        driver = webdriver.Edge(options=opts)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins',   { get: () => [1,2,3,4,5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['fr-MA','fr','en'] });
                window.chrome = { runtime: {} };
            """}
        )
        return driver

    # ── Helpers navigation ────────────────────────────────────────

    def delay(self, a=2.0, b=4.0):
        time.sleep(random.uniform(a, b))

    def scroll(self, driver):
        try:
            h = driver.execute_script("return document.body.scrollHeight")
            for i in range(random.randint(3, 5)):
                driver.execute_script(f"window.scrollTo(0,{int(h*(i+1)/5)});")
                time.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass

    def get_text(self, driver, *xpaths):
        for xp in xpaths:
            try:
                el = driver.find_element(By.XPATH, xp)
                t  = el.text.strip()
                if t:
                    return t
            except Exception:
                pass
        return "N/A"

    def get_links(self, driver, keyword, page=0):
        url = (f"https://www.emploi.ma/recherche-jobs-maroc"
               f"?search_api_views_fulltext={requests.utils.quote(keyword)}")
        if page > 0:
            url += f"&page={page}"
        driver.get(url)
        self.delay(3, 6)
        self.scroll(driver)
        self.delay(1, 2)
        return list(set([
            l.get_attribute('href')
            for l in driver.find_elements(
                By.XPATH, "//a[contains(@href,'offre-emploi-maroc')]"
            )
            if l.get_attribute('href')
        ]))

    # ── Scraping d'une offre ──────────────────────────────────────

    def scrape_one(self, driver, url):
        driver.get(url)
        self.delay(2, 5)
        self.scroll(driver)
        self.delay(1, 2)

        try:
            body = driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            body = ""
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1").text
        except Exception:
            h1 = "N/A"

        title    = h1.split('-')[0].strip() if '-' in h1 else h1.strip()
        company  = self.get_text(driver,
            "//div[contains(@class,'card-block-company')]//h3",
            "//span[contains(@class,'company')]"
        )
        location = self.get_text(driver,
            "//li[contains(@class,'location-dot')]//span",
            "//li[contains(@class,'location-dot')]"
        )
        sector   = self.get_text(driver,
            "//div[contains(@class,'field-name-field-entreprise-secteur')]"
            "//div[contains(@class,'field-item')]"
        )
        desc     = self.get_text(driver,
            "//*[contains(@class,'job-description')]",
            "//h3[contains(text(),'Poste propos')]/following-sibling::*[1]"
        )
        skills   = self.get_text(driver,
            "//*[contains(@class,'job-qualifications')]",
            "//h3[contains(text(),'Profil recherch')]/following-sibling::ul[1]"
        )
        educ = self.get_text(driver, "//li[contains(@class,'graduation-cap')]")
        exp  = self.get_text(driver, "//li[contains(@class,'chart')]")

        import re as _re
        date_str = None
        m = _re.search(r'(\d{2})\.(\d{2})\.(\d{4})', body)
        if m:
            date_str = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

        JobOffer.objects.create(
            title=self.clean(title)[:255],
            company=self.clean(company)[:255],
            location=self.clean(location),
            description=self.clean(desc)[:5000] if desc != "N/A" else self.clean(body)[:5000],
            required_skills=self.clean(skills) if skills != "N/A" else self.extract_skills(body),
            required_education=self.clean(educ) if educ != "N/A" else self.extract_education(body),
            required_experience=self.clean(exp) if exp != "N/A" else self.extract_experience(body),
            required_languages=self.extract_languages(body),
            contract_type=self.extract_contract(body),
            source="emploima",
            source_url=url,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f"    ✓ {title[:60]} ({company[:40]}) sauvegardé."))

    # ── Handle ────────────────────────────────────────────────────

    def handle(self, *args, **options):
        keyword_arg = options.get('keyword')
        limit       = options.get('limit') or EMPLOIMA_OFFERS

        keywords_to_search = [keyword_arg] if keyword_arg else KEYWORDS_LIST
        run_once           = bool(keyword_arg)

        self.stdout.write(self.style.SUCCESS(
            f"Démarrage du scraper Emploi.ma (Mot-clé: {keyword_arg or 'TOUS'})"
        ))

        while True:
            driver = None
            total  = 0
            try:
                driver  = self.get_driver()
                scraped = set()

                for keyword in keywords_to_search:
                    self.stdout.write(f"\n--- Recherche : '{keyword}' ---")
                    count      = 0
                    page       = 0
                    pages_done = 0
                    MAX_PAGES  = 3

                    while count < limit and pages_done < MAX_PAGES:
                        links     = self.get_links(driver, keyword, page)
                        new_links = [
                            l for l in links
                            if l not in scraped
                            and not JobOffer.objects.filter(source_url=l).exists()
                        ]

                        if not new_links:
                            page += 1
                            pages_done += 1
                            continue

                        for link in new_links:
                            if count >= limit:
                                break
                            try:
                                self.scrape_one(driver, link)
                                scraped.add(link)
                                count += 1
                                self.delay(1, 3)
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"    ✗ Erreur : {e}"))

                        page += 1
                        pages_done += 1
                        self.delay(2, 5)

                    total += count
                    self.stdout.write(f"  '{keyword}' → {count} offres sauvegardées.")

                if driver:
                    driver.quit()

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
                if driver:
                    driver.quit()
                if run_once:
                    break
                time.sleep(60)

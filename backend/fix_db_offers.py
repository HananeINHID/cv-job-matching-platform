"""
Script de nettoyage des offres en base de données.
- Corrige le champ contract_type pour Rekrute (extraire depuis la description)
- Corrige les required_skills vides (re-extraire depuis la description)
- Corrige les titres contenant des artefacts
"""
import django, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import JobOffer

# ─── Helpers ────────────────────────────────────────────────────────────────

SKILLS_LIST = [
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

def extract_contract(text):
    if not text:
        return ''
    t = text.lower()
    for c, kws in [
        ('CDI',        ['cdi']),
        ('CDD',        ['cdd']),
        ('Stage',      ['stage']),
        ('Freelance',  ['freelance']),
        ('Alternance', ['alternance']),
        ('Intérim',    ['intérim', 'interim']),
    ]:
        if any(k in t for k in kws):
            return c
    return ''

def extract_skills(text):
    if not text:
        return ''
    found = []
    for skill in SKILLS_LIST:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found.append(skill)
    return ', '.join(found[:8]) if found else ''

# ─── Fix 1 : Rekrute — contrat manquant ────────────────────────────────────

rekrute_no_contract = JobOffer.objects.filter(
    source='rekrute',
    contract_type__in=['Non spécifié', 'Non specifie', '']
)
print(f"Rekrute sans contrat : {rekrute_no_contract.count()} offres")
fixed_contract = 0
for o in rekrute_no_contract:
    text = (o.description or '') + ' ' + (o.title or '')
    ct = extract_contract(text)
    if ct:
        o.contract_type = ct
        o.save(update_fields=['contract_type'])
        fixed_contract += 1
print(f"  -> Contrats corrigés : {fixed_contract}")

# ─── Fix 2 : LinkedIn — contrat manquant ───────────────────────────────────

linkedin_no_contract = JobOffer.objects.filter(
    source='linkedin',
    contract_type__in=['Non spécifié', 'Non specifie', '']
)
print(f"\nLinkedIn sans contrat : {linkedin_no_contract.count()} offres")
fixed_linkedin_ct = 0
for o in linkedin_no_contract:
    text = (o.description or '') + ' ' + (o.title or '') + ' ' + (o.sector or '')
    ct = extract_contract(text)
    if ct:
        o.contract_type = ct
        o.save(update_fields=['contract_type'])
        fixed_linkedin_ct += 1
print(f"  -> Contrats corrigés : {fixed_linkedin_ct}")

# ─── Fix 3 : Skills manquants (toutes sources) ─────────────────────────────

no_skills = JobOffer.objects.filter(
    required_skills__in=['Non spécifié', 'Non specifie', '']
)
print(f"\nOffres sans skills : {no_skills.count()}")
fixed_skills = 0
for o in no_skills:
    text = (o.description or '') + ' ' + (o.title or '') + ' ' + (o.sector or '')
    sk = extract_skills(text)
    if sk:
        o.required_skills = sk
        o.save(update_fields=['required_skills'])
        fixed_skills += 1
print(f"  -> Skills corrigés : {fixed_skills}")

# ─── Fix 4 : Entreprise "N/A" → "Confidentiel" ─────────────────────────────

na_company = JobOffer.objects.filter(company__in=['N/A', 'n/a', ''])
print(f"\nEntreprises N/A : {na_company.count()}")
na_company.update(company='Confidentiel')
print(f"  -> Mis à jour en 'Confidentiel'")

# ─── Résumé final ───────────────────────────────────────────────────────────

print("\n=== RÉSUMÉ APRÈS NETTOYAGE ===")
for src in ['rekrute', 'emploima', 'marocannonces', 'linkedin']:
    total = JobOffer.objects.filter(source=src).count()
    no_ct = JobOffer.objects.filter(source=src, contract_type__in=['Non spécifié','Non specifie','']).count()
    no_sk = JobOffer.objects.filter(source=src, required_skills__in=['Non spécifié','Non specifie','']).count()
    print(f"  {src:<15}: {total} offres | sans contrat: {no_ct} | sans skills: {no_sk}")

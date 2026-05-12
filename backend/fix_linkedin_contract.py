"""
Fix LinkedIn contract_type : LinkedIn utilise des termes anglais (Full-time, Contract, Internship).
"""
import django, os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from api.models import JobOffer

def extract_contract_linkedin(text):
    if not text:
        return 'CDI'
    t = text.lower()
    mapping = [
        ('Stage',      ['internship', 'stage', 'stagiaire']),
        ('CDD',        ['cdd', 'fixed term', 'temporary', 'contract']),
        ('CDI',        ['cdi', 'full-time', 'full time', 'permanent']),
        ('Freelance',  ['freelance', 'self-employed', 'independent']),
        ('Alternance', ['alternance', 'apprenticeship']),
        ('Intérim',    ['interim', 'intérim', 'temp']),
    ]
    for label, kws in mapping:
        if any(k in t for k in kws):
            return label
    return 'CDI'  # défaut pour LinkedIn : la majorité des offres sont CDI

linkedin_no_ct = JobOffer.objects.filter(
    source='linkedin',
    contract_type__in=['Non spécifié', 'Non specifie', '']
)
print(f"LinkedIn sans contrat : {linkedin_no_ct.count()}")
fixed = 0
for o in linkedin_no_ct:
    text = ' '.join(filter(None, [o.description, o.title, o.sector]))
    ct = extract_contract_linkedin(text)
    o.contract_type = ct
    o.save(update_fields=['contract_type'])
    fixed += 1

print(f"  -> {fixed} offres mises à jour")

# Vérif finale
from django.db.models import Count
print("\n=== DISTRIBUTION CONTRATS LINKEDIN ===")
for row in JobOffer.objects.filter(source='linkedin').values('contract_type').annotate(n=Count('id')).order_by('-n'):
    print(f"  {row['contract_type']:<15}: {row['n']}")

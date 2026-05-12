import django, os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from api.models import JobOffer

print("=== ECHANTILLON REKRUTE ===")
for o in JobOffer.objects.filter(source='rekrute')[:5]:
    print(f"  {o.title[:45]} | {o.company[:20]} | {o.location[:15]}")
    print(f"    Skills: {str(o.required_skills)[:70]}")
    print(f"    Contrat: {o.contract_type} | Exp: {o.required_experience}")
    print()

print("=== ECHANTILLON EMPLOIMA ===")
for o in JobOffer.objects.filter(source='emploima')[:5]:
    print(f"  {o.title[:45]} | {o.company[:20]} | {o.location[:15]}")
    print(f"    Skills: {str(o.required_skills)[:70]}")
    desc_len = len(o.description or "")
    print(f"    Desc len: {desc_len} chars | Contrat: {o.contract_type}")
    print()

print("=== ECHANTILLON MAROCANNONCES ===")
for o in JobOffer.objects.filter(source='marocannonces')[:5]:
    print(f"  {o.title[:45]} | {o.company[:20]} | {o.location[:15]}")
    print(f"    Skills: {str(o.required_skills)[:70]}")
    print(f"    Contrat: {o.contract_type}")
    print()

print("=== STATS CONTRAT PAR SOURCE ===")
from django.db.models import Count
for src in ['rekrute','emploima','marocannonces','linkedin']:
    total = JobOffer.objects.filter(source=src).count()
    no_ct = JobOffer.objects.filter(source=src, contract_type__in=['Non specifie','Non spécifié','']).count()
    print(f"  {src}: {total} total, {no_ct} sans contrat")

print()
print("=== SKILLS VIDES PAR SOURCE ===")
for src in ['rekrute','emploima','marocannonces','linkedin']:
    total = JobOffer.objects.filter(source=src).count()
    no_sk = JobOffer.objects.filter(source=src, required_skills__in=['Non specifie','Non spécifié','']).count()
    print(f"  {src}: {total} total, {no_sk} sans skills")

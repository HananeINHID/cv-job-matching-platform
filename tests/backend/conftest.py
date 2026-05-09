"""
conftest.py — Configuration pytest globale pour les tests backend.

Fournit :
  - Fixtures de base (api_client, user, profil complet, offres d'emploi)
  - Configuration Django (SQLite en mémoire via pytest-django)
  - Fixtures JWT (client pré-authentifié)
"""

import json
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import UserProfile, Experience, Education, JobOffer, SearchHistory


# ─── Fixtures de base ─────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """APIClient DRF non authentifié."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory pour créer un User Django simple."""
    def _create(username="testuser", password="testpass123", email="test@example.com"):
        return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_active=True,
        )
    return _create


@pytest.fixture
def user(create_user):
    """User de base prêt à l'emploi."""
    return create_user()


@pytest.fixture
def user2(create_user):
    """Second user (pour tests d'isolation)."""
    return create_user(username="user2", email="user2@example.com")


@pytest.fixture
def authenticated_client(user):
    """APIClient DRF avec JWT valide dans le header Authorization."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def user_with_profile(user):
    """User Django + UserProfile complet avec compétences, expériences et formations."""
    profile = UserProfile.objects.create(
        user=user,
        nom="Hanane Test",
        email="hanane@test.com",
        telephone="+212 600000000",
        ville="Casablanca",
        titre="Développeuse Data Scientist",
        hard_skills=json.dumps(["python", "django", "sql", "machine learning"]),
        soft_skills=json.dumps(["communication", "travail en équipe"]),
        experience_years="3 ans",
        sector="Informatique",
        education_level="Master",
    )
    Experience.objects.create(
        profile=profile,
        poste="Data Analyst",
        entreprise="TechMaroc",
        debut="2022-01",
        fin="2024-01",
        description="Analyse de données et modélisation ML",
    )
    Education.objects.create(
        profile=profile,
        diplome="Master IASD",
        etablissement="FSS Marrakech",
        annee="2022",
        domaine="Intelligence Artificielle",
    )
    return user, profile


@pytest.fixture
def job_offers(db):
    """Crée 5 offres d'emploi variées (secteurs, villes, contrats différents)."""
    offres = [
        JobOffer.objects.create(
            title="Data Scientist",
            company="CAT Assurance",
            location="Casablanca",
            sector="Finance",
            description="Analyse de données financières avec Python et ML.",
            required_skills=json.dumps(["python", "sql", "machine learning", "pandas"]),
            required_experience="2 ans",
            contract_type="CDI",
            source="rekrute",
            source_url="https://rekrute.com/offre/1",
            is_active=True,
        ),
        JobOffer.objects.create(
            title="Développeur Django",
            company="WebAgency",
            location="Rabat",
            sector="IT",
            description="Développement backend Django REST Framework.",
            required_skills=json.dumps(["django", "python", "rest api", "postgresql"]),
            required_experience="1 an",
            contract_type="CDI",
            source="emploima",
            source_url="https://emploi.ma/offre/2",
            is_active=True,
        ),
        JobOffer.objects.create(
            title="Ingénieur BTP",
            company="Construire SA",
            location="Marrakech",
            sector="Construction",
            description="Gestion de chantiers et supervision des travaux de béton.",
            required_skills=json.dumps(["autocad", "béton", "chantier", "génie civil"]),
            required_experience="5 ans",
            contract_type="CDD",
            source="marocannonces",
            source_url="https://marocannonces.com/offre/3",
            is_active=True,
        ),
        JobOffer.objects.create(
            title="Frontend React Developer",
            company="StartupIO",
            location="Casablanca",
            sector="IT",
            description="Développement d'interfaces modernes avec React et TypeScript.",
            required_skills=json.dumps(["react", "javascript", "typescript", "css"]),
            required_experience="2 ans",
            contract_type="CDI",
            source="linkedin",
            source_url="https://linkedin.com/jobs/4",
            is_active=True,
        ),
        JobOffer.objects.create(
            title="Chef de Projet Digital",
            company="AgenceDigital",
            location="Casablanca",
            sector="Marketing",
            description="Pilotage de projets digitaux, coordination équipes tech et marketing.",
            required_skills=json.dumps(["gestion de projet", "agile", "scrum", "communication"]),
            required_experience="4 ans",
            contract_type="CDI",
            source="rekrute",
            source_url="https://rekrute.com/offre/5",
            is_active=True,
        ),
    ]
    return offres


@pytest.fixture
def search_history(user_with_profile):
    """Historique de recherches pour un user."""
    u, _ = user_with_profile
    entries = []
    for kw, src, cnt in [
        ("Data Scientist", "dataset", 12),
        ("Python Developer", "rekrute", 5),
        ("ML Engineer", "emploima", 8),
    ]:
        entries.append(SearchHistory.objects.create(
            user=u, keyword=kw, source=src, results_count=cnt
        ))
    return entries

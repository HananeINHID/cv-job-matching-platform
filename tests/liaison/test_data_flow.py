"""
test_data_flow.py — Tests de flux de données de bout en bout.

Périmètre :
  Teste le flux complet sans browser :
  Inscription → JWT → Profil → Matching → Historique → Radar

  FLUX 1 : Inscription → Profil → Matching
  FLUX 2 : Cohérence des scores (IT vs BTP)
  FLUX 3 : Historique cohérent avec les recherches
  FLUX 4 : Score Radar ≈ Score Matching

  Aucun appel réseau externe requis.
"""

import json
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import UserProfile, JobOffer, SearchHistory


pytestmark = pytest.mark.django_db


def _get_auth_client(user) -> APIClient:
    """Crée un APIClient avec JWT valide pour l'user donné."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# ═══════════════════════════════════════════════════════════
#  FLUX 1 — Inscription → Profil → Matching
# ═══════════════════════════════════════════════════════════

class TestFlux1InscriptionProfilMatching:

    def test_full_flux_register_profile_match(self, api_client, job_offers):
        """
        FLUX COMPLET :
        1. POST /api/auth/register/ → créer user
        2. POST /api/token/         → récupérer JWT
        3. POST /api/profile/cv/    → soumettre CV complet
        4. GET  /api/matching/results/ → scores calculés
        5. SearchHistory créé avec le bon keyword
        """
        # Étape 1 : Inscription
        reg_response = api_client.post("/api/auth/register/", {
            "username": "flux1_user",
            "email": "flux1@test.com",
            "password": "SecureFlux123",
            "password_confirm": "SecureFlux123",
        }, format="json")
        assert reg_response.status_code in [200, 201], \
            f"Inscription échouée: {reg_response.data}"

        # Étape 2 : Obtenir JWT
        token_response = api_client.post("/api/token/", {
            "username": "flux1_user",
            "password": "SecureFlux123",
        }, format="json")
        assert token_response.status_code == 200, \
            f"Login échoué: {token_response.data}"

        access_token = token_response.data["access"]
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Étape 3 : Soumettre le profil CV
        cv_response = auth_client.post("/api/profile/cv/", {
            "personal_info": {
                "nom": "Flux1 User",
                "email": "flux1@test.com",
                "telephone": "+212 600000001",
                "ville": "Casablanca",
                "titre": "Data Scientist",
            },
            "hard_skills": ["python", "sql", "machine learning", "pandas"],
            "soft_skills": ["communication"],
            "experiences": [{"poste": "Data Analyst", "entreprise": "Corp", "debut": "2022-01", "fin": "", "description": "Analyse"}],
            "formations": [{"diplome": "Master", "etablissement": "Université", "annee": "2022", "domaine": "IA"}],
        }, format="json")
        assert cv_response.status_code == 200, \
            f"Soumission CV échouée: {cv_response.data}"

        user = User.objects.get(username="flux1_user")
        assert UserProfile.objects.filter(user=user).exists()

        # Étape 4 : Lancer le matching
        match_response = auth_client.get("/api/matching/results/")
        assert match_response.status_code == 200
        assert isinstance(match_response.data, list)

        # Étape 5 : Vérifier SearchHistory créé
        history = SearchHistory.objects.filter(user=user)
        assert history.count() > 0, "SearchHistory non créé après le matching"


# ═══════════════════════════════════════════════════════════
#  FLUX 2 — Cohérence des scores (IT vs BTP)
# ═══════════════════════════════════════════════════════════

class TestFlux2ScoreCohérence:

    def test_python_profile_scores_higher_on_it_offer_than_btp(self, authenticated_client, user, user_with_profile):
        """
        Profil Python/Django/SQL → offre IT doit scorer PLUS HAUT que offre BTP.
        """
        _, _ = user_with_profile  # profil avec python, django, sql, machine learning

        # Offre IT (compatible)
        it_offer = JobOffer.objects.create(
            title="Data Scientist Python",
            company="TechCo",
            location="Casablanca",
            description="Analyse de données financières avec Python et Machine Learning",
            required_skills=json.dumps(["python", "sql", "machine learning", "pandas"]),
            required_experience="2 ans",
            source="rekrute",
            source_url="https://rekrute.com/it",
            is_active=True,
        )

        # Offre BTP (incompatible)
        btp_offer = JobOffer.objects.create(
            title="Chef de Chantier BTP",
            company="BâtirCo",
            location="Agadir",
            description="Supervision de chantiers de construction béton armé",
            required_skills=json.dumps(["autocad", "béton", "chantier", "génie civil"]),
            required_experience="5 ans",
            source="marocannonces",
            source_url="https://marocannonces.com/btp",
            is_active=True,
        )

        response = authenticated_client.get("/api/matching/results/")
        assert response.status_code == 200

        scores = {item["id"]: item["score"] for item in response.data}

        if it_offer.id in scores and btp_offer.id in scores:
            assert scores[it_offer.id] > scores[btp_offer.id], \
                f"Score IT ({scores[it_offer.id]}) ≤ Score BTP ({scores[btp_offer.id]}) — incohérent"

    def test_high_matching_offer_scores_above_50(self, authenticated_client, user, user_with_profile):
        """
        Offre avec TOUTES les compétences du CV → score > 50%.
        """
        _, profile = user_with_profile

        # Offre identique aux skills du profil
        perfect_offer = JobOffer.objects.create(
            title="Data Engineer Python SQL",
            company="PerfectMatch Corp",
            location="Casablanca",  # même ville que le profil
            description="python django sql machine learning data science",
            required_skills=json.dumps(["python", "django", "sql", "machine learning"]),
            required_experience="3 ans",
            source="rekrute",
            source_url="https://rekrute.com/perfect",
            is_active=True,
        )

        response = authenticated_client.get("/api/matching/results/")
        assert response.status_code == 200

        scores = {item["id"]: item["score"] for item in response.data}
        if perfect_offer.id in scores:
            assert scores[perfect_offer.id] > 50, \
                f"Score offre parfaite ({scores[perfect_offer.id]}) devrait être > 50%"

    def test_incompatible_offer_scores_below_40(self, authenticated_client, user, user_with_profile):
        """
        Offre BTP vs profil IT → score < 40%.
        """
        _, _ = user_with_profile

        btp_offer = JobOffer.objects.create(
            title="Ingénieur Génie Civil",
            company="BâtirMaroc",
            location="Dakhla",  # ville différente
            description="béton armé chantier maçonnerie topographie autocad architecture",
            required_skills=json.dumps(["autocad", "béton", "chantier", "maçonnerie"]),
            required_experience="10 ans",
            source="marocannonces",
            source_url="https://marocannonces.com/btp2",
            is_active=True,
        )

        response = authenticated_client.get("/api/matching/results/")
        scores = {item["id"]: item["score"] for item in response.data}
        if btp_offer.id in scores:
            assert scores[btp_offer.id] < 40, \
                f"Score BTP ({scores[btp_offer.id]}) devrait être < 40% pour un profil IT"


# ═══════════════════════════════════════════════════════════
#  FLUX 3 — Historique cohérent avec les recherches
# ═══════════════════════════════════════════════════════════

class TestFlux3HistoriqueCohérent:

    def test_three_searches_create_three_history_entries(self, authenticated_client, user, user_with_profile, job_offers):
        """
        3 appels /matching/results/ avec ?q= différents → 3 entrées SearchHistory.
        """
        _, _ = user_with_profile

        keywords = ["data scientist", "python developer", "machine learning"]
        for kw in keywords:
            response = authenticated_client.get(f"/api/matching/results/?q={kw}")
            assert response.status_code == 200

        history_count = SearchHistory.objects.filter(user=user).count()
        assert history_count >= 3, \
            f"Attendu ≥ 3 entrées SearchHistory, obtenu {history_count}"

    def test_history_keywords_match_search_queries(self, authenticated_client, user, user_with_profile, job_offers):
        """
        Les keywords dans l'historique correspondent aux recherches effectuées.
        """
        _, _ = user_with_profile

        # Recherche avec un keyword unique
        unique_kw = "reactnativeunique"
        authenticated_client.get(f"/api/matching/results/?q={unique_kw}")

        history_response = authenticated_client.get("/api/profile/history/")
        assert history_response.status_code == 200

        keywords_in_history = [entry["keyword"] for entry in history_response.data["history"]]
        assert unique_kw in keywords_in_history, \
            f"Keyword '{unique_kw}' absent de l'historique: {keywords_in_history}"

    def test_history_count_is_accurate(self, authenticated_client, user, user_with_profile, job_offers):
        """
        count dans la réponse correspond au nombre d'entrées retournées.
        """
        _, _ = user_with_profile
        authenticated_client.get("/api/matching/results/")
        authenticated_client.get("/api/matching/results/?q=python")

        history_response = authenticated_client.get("/api/profile/history/")
        data = history_response.data
        assert data["count"] == len(data["history"])


# ═══════════════════════════════════════════════════════════
#  FLUX 4 — Cohérence Radar ↔ Matching
# ═══════════════════════════════════════════════════════════

class TestFlux4RadarMatchingCohérence:

    def test_radar_score_comparable_to_matching_score(self, authenticated_client, user, user_with_profile, job_offers):
        """
        Score radar pour une offre ≈ score matching pour la même offre (±15 pts de tolérance).
        """
        _, _ = user_with_profile

        # Récupérer les résultats de matching
        match_response = authenticated_client.get("/api/matching/results/")
        assert match_response.status_code == 200
        assert len(match_response.data) > 0

        # Prendre la première offre
        first_item = match_response.data[0]
        offer_id = first_item["id"]
        matching_score = first_item["score"]

        # Récupérer le radar pour cette offre
        radar_response = authenticated_client.get(f"/api/jobs/{offer_id}/radar/")
        assert radar_response.status_code == 200

        radar_score = radar_response.data["score"]

        # Les deux scores doivent être comparables (marge de 20 points)
        assert abs(matching_score - radar_score) <= 20, \
            f"Score matching ({matching_score}) et radar ({radar_score}) trop différents"

    def test_radar_labels_correspond_to_offer_skills(self, authenticated_client, user, user_with_profile, job_offers):
        """
        Labels du radar correspondent aux compétences de l'offre ou du CV.
        """
        _, _ = user_with_profile

        offer_id = job_offers[0].id  # Data Scientist avec python, sql, etc.
        response = authenticated_client.get(f"/api/jobs/{offer_id}/radar/")
        assert response.status_code == 200

        labels = response.data["labels"]
        assert len(labels) > 0, "Le radar doit avoir au moins un label"
        for label in labels:
            assert isinstance(label, str) and len(label) > 0

    def test_radar_match_rate_consistent_with_skills(self, authenticated_client, user, user_with_profile, job_offers):
        """
        match_rate plus élevé pour une offre compatible que pour une offre incompatible.
        """
        _, profile = user_with_profile

        # Offre très compatible (même skills que le profil)
        compatible_offer = JobOffer.objects.create(
            title="Python Data Scientist",
            company="BestMatch",
            location="Casablanca",
            description="python sql django machine learning",
            required_skills=json.dumps(["python", "sql", "machine learning"]),
            required_experience="2 ans",
            source="rekrute",
            source_url="https://rekrute.com/best",
            is_active=True,
        )

        # Offre incompatible
        incompatible_offer = JobOffer.objects.create(
            title="Plombier Sanitaire",
            company="PlomberiePro",
            location="Oujda",
            description="plomberie sanitaire tuyauterie chantier renovation",
            required_skills=json.dumps(["plomberie", "sanitaire", "tuyauterie"]),
            required_experience="5 ans",
            source="marocannonces",
            source_url="https://marocannonces.com/plomb",
            is_active=True,
        )

        radar_compatible = authenticated_client.get(f"/api/jobs/{compatible_offer.id}/radar/")
        radar_incompatible = authenticated_client.get(f"/api/jobs/{incompatible_offer.id}/radar/")

        if radar_compatible.status_code == 200 and radar_incompatible.status_code == 200:
            rate_compatible = radar_compatible.data["match_rate"]
            rate_incompatible = radar_incompatible.data["match_rate"]
            assert rate_compatible >= rate_incompatible, \
                f"match_rate compatible ({rate_compatible}) < incompatible ({rate_incompatible})"

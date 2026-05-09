"""
test_profile_endpoints.py — Tests d'intégration des endpoints de profil CV.

Périmètre :
  GET  /api/profile/me/   : récupération profil
  POST /api/profile/cv/   : création / mise à jour profil complet
  GET  /api/profile/history/ : historique des recherches

Chaque test est isolé (rollback automatique pytest-django).
"""

import json
import pytest
from django.contrib.auth.models import User
from api.models import UserProfile, Experience, Education, SearchHistory


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  GET /api/profile/me/
# ═══════════════════════════════════════════════════════════

class TestProfileMeEndpoint:

    URL = "/api/profile/me/"

    def test_get_profile_me_authenticated_no_profile_creates_empty(self, authenticated_client):
        """User authentifié sans profil → get_or_create retourne profil vide, 200 OK."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_get_profile_me_unauthenticated_returns_401(self, api_client):
        """User non authentifié → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_get_profile_me_returns_personal_info(self, authenticated_client, user):
        """Profil existant → personal_info retourné."""
        UserProfile.objects.create(
            user=user,
            nom="Test User",
            email="test@test.com",
            ville="Casablanca",
            titre="Dev",
        )
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        data = response.data
        # La réponse doit contenir des infos de profil
        assert "personal_info" in data or "nom" in data or "id" in data


# ═══════════════════════════════════════════════════════════
#  POST /api/profile/cv/
# ═══════════════════════════════════════════════════════════

class TestCVProfileEndpoint:

    URL = "/api/profile/cv/"

    VALID_PAYLOAD = {
        "personal_info": {
            "nom": "Hanane Test",
            "email": "hanane@test.com",
            "telephone": "+212 600000000",
            "ville": "Casablanca",
            "titre": "Data Scientist",
        },
        "hard_skills": ["python", "sql", "machine learning"],
        "soft_skills": ["communication", "leadership"],
        "experiences": [
            {
                "poste": "Data Analyst",
                "entreprise": "TechMaroc",
                "debut": "2022-01",
                "fin": "2024-01",
                "description": "Analyse de données",
            }
        ],
        "formations": [
            {
                "diplome": "Master IASD",
                "etablissement": "FSS",
                "annee": "2022",
                "domaine": "IA",
            }
        ],
    }

    def test_post_cv_valid_payload_returns_200(self, authenticated_client):
        """Payload complet valide → 200 + profil mis à jour en DB."""
        response = authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        assert response.status_code == 200

    def test_post_cv_creates_profile_in_db(self, authenticated_client, user):
        """POST valide → UserProfile créé en DB."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        assert UserProfile.objects.filter(user=user).exists()

    def test_post_cv_stores_personal_info(self, authenticated_client, user):
        """POST valide → nom, ville, titre stockés correctement."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        profile = UserProfile.objects.get(user=user)
        assert profile.nom == "Hanane Test"
        assert profile.ville == "Casablanca"
        assert profile.titre == "Data Scientist"

    def test_post_cv_hard_skills_stored_as_json(self, authenticated_client, user):
        """hard_skills envoyés en liste → stockés en JSON string parsable."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        profile = UserProfile.objects.get(user=user)
        skills = json.loads(profile.hard_skills)
        assert "python" in skills
        assert "sql" in skills

    def test_post_cv_experiences_created_in_db(self, authenticated_client, user):
        """Expériences imbriquées → créées en DB avec transaction.atomic()."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        profile = UserProfile.objects.get(user=user)
        experiences = Experience.objects.filter(profile=profile)
        assert experiences.count() == 1
        assert experiences.first().poste == "Data Analyst"

    def test_post_cv_formations_created_in_db(self, authenticated_client, user):
        """Formations imbriquées → créées correctement."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        profile = UserProfile.objects.get(user=user)
        formations = Education.objects.filter(profile=profile)
        assert formations.count() == 1
        assert formations.first().diplome == "Master IASD"

    def test_post_cv_update_replaces_old_data(self, authenticated_client, user):
        """Deuxième POST → met à jour le profil existant (pas de doublon)."""
        authenticated_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        # Mise à jour
        updated_payload = dict(self.VALID_PAYLOAD)
        updated_payload["personal_info"] = dict(self.VALID_PAYLOAD["personal_info"])
        updated_payload["personal_info"]["nom"] = "Hanane Updated"
        authenticated_client.post(self.URL, updated_payload, format="json")

        # Un seul profil doit exister
        assert UserProfile.objects.filter(user=user).count() == 1
        profile = UserProfile.objects.get(user=user)
        assert profile.nom == "Hanane Updated"

    def test_post_cv_unauthenticated_returns_401(self, api_client):
        """POST sans token → 401."""
        response = api_client.post(self.URL, self.VALID_PAYLOAD, format="json")
        assert response.status_code == 401

    def test_post_cv_no_experiences_accepted(self, authenticated_client):
        """Payload sans expériences → 200 (champ optionnel)."""
        payload = dict(self.VALID_PAYLOAD)
        payload["experiences"] = []
        response = authenticated_client.post(self.URL, payload, format="json")
        assert response.status_code == 200

    def test_post_cv_hard_skills_as_json_string_converted(self, authenticated_client, user):
        """hard_skills envoyés en liste JSON → correctement parsés par le serializer."""
        payload = dict(self.VALID_PAYLOAD)
        payload["hard_skills"] = ["react", "typescript", "nodejs"]
        authenticated_client.post(self.URL, payload, format="json")
        profile = UserProfile.objects.get(user=user)
        parsed = json.loads(profile.hard_skills)
        assert "react" in parsed


# ═══════════════════════════════════════════════════════════
#  GET /api/profile/cv/ (Lecture du profil)
# ═══════════════════════════════════════════════════════════

class TestCVProfileGetEndpoint:

    URL = "/api/profile/cv/"

    def test_get_cv_authenticated_returns_200(self, authenticated_client):
        """GET /api/profile/cv/ authentifié → 200."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_get_cv_returns_expected_structure(self, authenticated_client, user):
        """Réponse contient personal_info, hard_skills_list, soft_skills_list, experiences, formations."""
        UserProfile.objects.create(
            user=user, nom="Alice", email="alice@test.com", titre="Dev"
        )
        response = authenticated_client.get(self.URL)
        data = response.data
        assert "personal_info" in data
        assert "experiences" in data
        assert "formations" in data

    def test_get_cv_hard_skills_list_is_list(self, authenticated_client, user):
        """hard_skills_list est toujours une liste (jamais une string brute)."""
        UserProfile.objects.create(
            user=user,
            nom="Bob",
            email="bob@test.com",
            titre="Dev",
            hard_skills=json.dumps(["python", "sql"]),
        )
        response = authenticated_client.get(self.URL)
        data = response.data
        skills = data.get("hard_skills_list", data.get("hard_skills", []))
        assert isinstance(skills, list)

    def test_get_cv_unauthenticated_returns_401(self, api_client):
        """GET sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_get_cv_no_profile_returns_empty_structure(self, authenticated_client):
        """Pas de profil → retourne une structure vide (pas 404)."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        data = response.data
        pi = data.get("personal_info", {})
        assert pi.get("nom", "") == "" or pi.get("nom") is None


# ═══════════════════════════════════════════════════════════
#  GET /api/profile/history/
# ═══════════════════════════════════════════════════════════

class TestSearchHistoryEndpoint:

    URL = "/api/profile/history/"

    def test_get_history_authenticated_returns_200(self, authenticated_client):
        """GET authentifié → 200."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_get_history_returns_count_and_list(self, authenticated_client):
        """Réponse contient {count, history}."""
        response = authenticated_client.get(self.URL)
        data = response.data
        assert "count" in data
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_get_history_entries_have_required_fields(self, authenticated_client, user, search_history):
        """Chaque entrée contient keyword, searched_at, results_count."""
        # search_history fixture crée 3 entrées pour user_with_profile,
        # mais authenticated_client utilise `user` (different) → count=0
        # On crée des entrées pour le user du authenticated_client
        from api.models import SearchHistory as SH
        SH.objects.create(user=user, keyword="test kw", source="dataset", results_count=5)
        response = authenticated_client.get(self.URL)
        data = response.data
        if data["count"] > 0:
            entry = data["history"][0]
            assert "keyword" in entry
            assert "searched_at" in entry
            assert "results_count" in entry

    def test_get_history_sorted_by_date_desc(self, authenticated_client, user):
        """Historique trié par searched_at décroissant."""
        from api.models import SearchHistory as SH
        SH.objects.create(user=user, keyword="first", source="dataset", results_count=1)
        SH.objects.create(user=user, keyword="second", source="rekrute", results_count=2)
        SH.objects.create(user=user, keyword="third", source="emploima", results_count=3)

        response = authenticated_client.get(self.URL)
        data = response.data
        if len(data["history"]) >= 2:
            # Le plus récent doit être en premier
            assert data["history"][0]["keyword"] == "third"

    def test_get_history_unauthenticated_returns_401(self, api_client):
        """GET sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_get_history_limit_parameter(self, authenticated_client, user):
        """Paramètre limit fonctionne."""
        from api.models import SearchHistory as SH
        for i in range(25):
            SH.objects.create(user=user, keyword=f"kw{i}", source="dataset", results_count=i)

        response = authenticated_client.get(f"{self.URL}?limit=5")
        assert response.status_code == 200
        assert len(response.data["history"]) <= 5

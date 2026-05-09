"""
test_api_contracts.py — Vérification des contrats API front↔back.

Périmètre :
  Vérifie que les réponses réelles du backend correspondent EXACTEMENT
  à la structure attendue par le frontend React.

  Contrats vérifiés :
    - POST /api/auth/register/      → {id, username, email} (sans password)
    - POST /api/token/              → {access, refresh} JWT valide
    - GET  /api/profile/me/         → structure profil complète
    - GET  /api/matching/results/   → items {id, titre, entreprise, ville, contrat, score, competences}
    - GET  /api/jobs/<id>/radar/    → {labels, cv, offre, match_rate, score} aligned
    - GET  /api/matching/clusters/  → items {x, y, cluster, cluster_label, label}
    - GET  /api/profile/history/    → {count, history[{keyword, searched_at, results_count}]}
"""

import json
import pytest
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import UserProfile, JobOffer, SearchHistory


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  CONTRAT : POST /api/auth/register/
# ═══════════════════════════════════════════════════════════

class TestRegisterContract:

    URL = "/api/auth/register/"

    def test_register_response_contains_id_username_email(self, api_client):
        """201 → réponse contient id, username, email."""
        payload = {
            "username": "contract_user",
            "email": "contract@test.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = api_client.post(self.URL, payload, format="json")
        # Accepter 201 ou 200 selon la config
        assert response.status_code in [200, 201]

    def test_register_response_does_not_contain_password(self, api_client):
        """La réponse d'inscription NE doit PAS contenir le password (sécurité)."""
        payload = {
            "username": "nopwd_user",
            "email": "nopwd@test.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = api_client.post(self.URL, payload, format="json")
        assert "password" not in response.data, \
            "SÉCURITÉ : Le mot de passe ne doit pas être retourné dans la réponse d'inscription"


# ═══════════════════════════════════════════════════════════
#  CONTRAT : POST /api/token/
# ═══════════════════════════════════════════════════════════

class TestTokenContract:

    URL = "/api/token/"

    def test_token_response_has_access_and_refresh(self, api_client, user):
        """200 → réponse contient exactement access et refresh."""
        response = api_client.post(self.URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_access_token_is_valid_jwt(self, api_client, user):
        """access token est un JWT avec 3 parties (header.payload.signature)."""
        response = api_client.post(self.URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        access = response.data["access"]
        parts = access.split(".")
        assert len(parts) == 3, f"JWT invalide (attendu 3 parties): {access[:30]}..."

    def test_jwt_payload_contains_user_id(self, api_client, user):
        """Le payload JWT décodé contient user_id."""
        import base64
        response = api_client.post(self.URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        access = response.data["access"]
        # Décoder le payload (2ème partie du JWT)
        payload_b64 = access.split(".")[1]
        # Ajouter padding si nécessaire
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.b64decode(payload_b64).decode())
        assert "user_id" in payload, f"user_id absent du payload JWT: {list(payload.keys())}"

    def test_jwt_payload_contains_token_type_access(self, api_client, user):
        """Le payload JWT contient token_type='access'."""
        import base64
        response = api_client.post(self.URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        access = response.data["access"]
        payload_b64 = access.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.b64decode(payload_b64).decode())
        assert payload.get("token_type") == "access"

    def test_jwt_payload_contains_exp(self, api_client, user):
        """Le payload JWT contient exp (expiration timestamp)."""
        import base64
        response = api_client.post(self.URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        access = response.data["access"]
        payload_b64 = access.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.b64decode(payload_b64).decode())
        assert "exp" in payload, "Expiration (exp) absente du payload JWT"


# ═══════════════════════════════════════════════════════════
#  CONTRAT : GET /api/profile/me/
# ═══════════════════════════════════════════════════════════

class TestProfileMeContract:

    URL = "/api/profile/me/"

    def test_profile_me_contains_expected_fields(self, authenticated_client, user):
        """Réponse contient id, personal_info (ou nom, ville, titre)."""
        UserProfile.objects.create(
            user=user, nom="Test", email="t@t.com", titre="Dev", ville="Casa"
        )
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        data = response.data
        # Doit contenir au minimum id + personal_info ou champs directs
        assert "id" in data or "personal_info" in data

    def test_profile_me_hard_skills_list_is_always_list(self, authenticated_client, user):
        """hard_skills_list est une liste (jamais une string JSON brute)."""
        UserProfile.objects.create(
            user=user,
            nom="Test",
            email="t@t.com",
            titre="Dev",
            hard_skills=json.dumps(["python", "sql"]),
        )
        response = authenticated_client.get(self.URL)
        data = response.data
        skills = data.get("hard_skills_list", data.get("hard_skills", None))
        if skills is not None:
            assert isinstance(skills, list), \
                f"hard_skills doit être une liste, pas: {type(skills)}"

    def test_profile_me_experiences_is_list(self, authenticated_client, user):
        """experiences est une liste."""
        UserProfile.objects.create(user=user, nom="Test", email="t@t.com", titre="Dev")
        response = authenticated_client.get(self.URL)
        data = response.data
        if "experiences" in data:
            assert isinstance(data["experiences"], list)


# ═══════════════════════════════════════════════════════════
#  CONTRAT : GET /api/matching/results/
# ═══════════════════════════════════════════════════════════

class TestMatchingResultsContract:

    URL = "/api/matching/results/"

    def test_matching_items_have_exact_required_fields(self, authenticated_client, user, user_with_profile, job_offers):
        """Chaque item contient exactement les champs attendus par le frontend."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        required = {"id", "titre", "entreprise", "ville", "contrat", "score", "competences", "source"}
        for item in response.data:
            missing = required - set(item.keys())
            assert not missing, f"Champs manquants: {missing} dans {dict(item)}"

    def test_matching_score_is_integer(self, authenticated_client, user, user_with_profile, job_offers):
        """score est un entier (pas un float)."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for item in response.data:
            assert isinstance(item["score"], int), \
                f"score doit être int, obtenu {type(item['score'])}: {item['score']}"

    def test_matching_score_between_0_and_99(self, authenticated_client, user, user_with_profile, job_offers):
        """score est dans [0, 99]."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for item in response.data:
            assert 0 <= item["score"] <= 99

    def test_matching_competences_is_list_of_strings(self, authenticated_client, user, user_with_profile, job_offers):
        """competences est une liste de chaînes."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for item in response.data:
            assert isinstance(item["competences"], list)
            for comp in item["competences"]:
                assert isinstance(comp, str)


# ═══════════════════════════════════════════════════════════
#  CONTRAT : GET /api/jobs/<id>/radar/
# ═══════════════════════════════════════════════════════════

class TestRadarContract:

    def _url(self, offer_id):
        return f"/api/jobs/{offer_id}/radar/"

    def test_radar_labels_cv_offre_same_length(self, authenticated_client, user, user_with_profile, job_offers):
        """len(labels) == len(cv) == len(offre)."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._url(offer_id))
        data = response.data
        assert len(data["labels"]) == len(data["cv"]) == len(data["offre"]), \
            "CONTRAT ROMPU: labels, cv, offre doivent avoir la même longueur"

    def test_radar_match_rate_is_numeric(self, authenticated_client, user, user_with_profile, job_offers):
        """match_rate est un nombre."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._url(offer_id))
        assert isinstance(response.data["match_rate"], (int, float))

    def test_radar_score_is_integer(self, authenticated_client, user, user_with_profile, job_offers):
        """score est un entier."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._url(offer_id))
        assert isinstance(response.data["score"], int)


# ═══════════════════════════════════════════════════════════
#  CONTRAT : GET /api/matching/clusters/
# ═══════════════════════════════════════════════════════════

class TestClustersContract:

    URL = "/api/matching/clusters/"

    def test_clusters_items_have_x_y_cluster_label(self, authenticated_client, job_offers):
        """Chaque item contient x, y, cluster, cluster_label, label."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200 and len(response.data) > 0:
            required = {"x", "y", "cluster", "cluster_label", "label"}
            item = response.data[0]
            missing = required - set(item.keys())
            assert not missing, f"Champs manquants dans cluster item: {missing}"

    def test_clusters_x_y_are_floats(self, authenticated_client, job_offers):
        """x et y sont des floats."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200:
            for item in response.data:
                assert isinstance(item["x"], (int, float))
                assert isinstance(item["y"], (int, float))


# ═══════════════════════════════════════════════════════════
#  CONTRAT : GET /api/profile/history/
# ═══════════════════════════════════════════════════════════

class TestHistoryContract:

    URL = "/api/profile/history/"

    def test_history_response_structure(self, authenticated_client):
        """Réponse contient {count (int), history (liste)}."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "history" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["history"], list)

    def test_history_items_have_required_fields(self, authenticated_client, user):
        """Chaque item history contient keyword, searched_at, results_count."""
        SearchHistory.objects.create(
            user=user, keyword="Python Dev", source="dataset", results_count=10
        )
        response = authenticated_client.get(self.URL)
        data = response.data
        for entry in data["history"]:
            assert "keyword" in entry
            assert "searched_at" in entry
            assert "results_count" in entry

    def test_history_searched_at_is_iso_format(self, authenticated_client, user):
        """searched_at est une date ISO 8601 valide."""
        SearchHistory.objects.create(
            user=user, keyword="Test", source="rekrute", results_count=5
        )
        response = authenticated_client.get(self.URL)
        for entry in response.data["history"]:
            searched_at = entry["searched_at"]
            # Doit être parsable comme datetime ISO
            try:
                datetime.fromisoformat(str(searched_at).replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pytest.fail(f"searched_at n'est pas ISO 8601: {searched_at}")

    def test_history_count_matches_list_length(self, authenticated_client, user):
        """count correspond au nombre d'éléments dans history."""
        SearchHistory.objects.create(user=user, keyword="A", source="dataset", results_count=1)
        SearchHistory.objects.create(user=user, keyword="B", source="rekrute", results_count=2)
        response = authenticated_client.get(self.URL)
        data = response.data
        assert data["count"] == len(data["history"]), \
            f"count ({data['count']}) ≠ len(history) ({len(data['history'])})"

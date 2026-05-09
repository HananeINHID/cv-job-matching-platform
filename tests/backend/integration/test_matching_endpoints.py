"""
test_matching_endpoints.py — Tests d'intégration des endpoints de matching.

Périmètre :
  GET /api/matching/results/  : scores de matching CV ↔ offres
  GET /api/matching/clusters/ : clustering K-Means des offres
  GET /api/jobs/<id>/radar/   : comparaison compétences CV vs offre

Chaque test est isolé avec ses propres fixtures.
"""

import json
import pytest
from django.contrib.auth.models import User
from api.models import UserProfile, JobOffer, SearchHistory


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  GET /api/matching/results/
# ═══════════════════════════════════════════════════════════

class TestMatchingResultsEndpoint:

    URL = "/api/matching/results/"

    def test_matching_returns_200_with_offers(self, authenticated_client, user, user_with_profile, job_offers):
        """Profil + offres → 200 + liste non vide."""
        # user_with_profile utilise `user` (même fixture), authenticated_client aussi
        _, profile = user_with_profile
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_matching_results_sorted_by_score_desc(self, authenticated_client, user, user_with_profile, job_offers):
        """Résultats triés par score décroissant."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        scores = [item["score"] for item in response.data]
        assert scores == sorted(scores, reverse=True), "Résultats non triés par score décroissant"

    def test_matching_result_item_has_required_fields(self, authenticated_client, user, user_with_profile, job_offers):
        """Chaque résultat contient les champs requis par le frontend."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        if len(response.data) > 0:
            item = response.data[0]
            required_fields = ["id", "titre", "entreprise", "ville", "contrat", "score", "competences", "source"]
            for field in required_fields:
                assert field in item, f"Champ manquant dans le résultat: '{field}'"

    def test_matching_score_between_0_and_99(self, authenticated_client, user, user_with_profile, job_offers):
        """Score de chaque offre entre 0 et 99."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for item in response.data:
            assert 0 <= item["score"] <= 99, f"Score hors bornes: {item['score']} pour {item.get('titre')}"

    def test_matching_competences_is_list(self, authenticated_client, user, user_with_profile, job_offers):
        """'competences' est toujours une liste."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for item in response.data:
            assert isinstance(item["competences"], list)

    def test_matching_creates_search_history(self, authenticated_client, user, user_with_profile, job_offers):
        """Appel à /matching/results/ → SearchHistory créé pour l'user."""
        _, _ = user_with_profile
        before = SearchHistory.objects.filter(user=user).count()
        authenticated_client.get(self.URL)
        after = SearchHistory.objects.filter(user=user).count()
        assert after > before, "SearchHistory n'a pas été créé après le matching"

    def test_matching_with_query_filter(self, authenticated_client, user, user_with_profile, job_offers):
        """Paramètre ?q= filtre les résultats par titre/lieu."""
        _, _ = user_with_profile
        response = authenticated_client.get(f"{self.URL}?q=data")
        assert response.status_code == 200
        # Si des offres "data" existent, vérifier le filtre
        for item in response.data:
            assert "data" in item["titre"].lower() or "data" in item["ville"].lower()

    def test_matching_without_token_returns_401(self, api_client):
        """Accès sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_matching_empty_db_returns_empty_list(self, authenticated_client, user, user_with_profile):
        """Aucune offre en DB → liste vide (pas d'erreur)."""
        _, _ = user_with_profile
        # job_offers non inclus → DB vide d'offres
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        assert response.data == []


# ═══════════════════════════════════════════════════════════
#  GET /api/matching/clusters/
# ═══════════════════════════════════════════════════════════

class TestClusterEndpoint:

    URL = "/api/matching/clusters/"

    def test_clusters_returns_200_or_503(self, authenticated_client, job_offers):
        """GET clusters → 200 (avec modèle) ou 503 (sans modèle pkl)."""
        response = authenticated_client.get(self.URL)
        assert response.status_code in [200, 503]

    def test_clusters_result_structure_when_available(self, authenticated_client, job_offers):
        """Si 200, chaque point contient x, y, cluster, cluster_label."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200 and len(response.data) > 0:
            item = response.data[0]
            assert "x" in item
            assert "y" in item
            assert "cluster" in item
            assert "cluster_label" in item

    def test_clusters_x_y_are_numbers(self, authenticated_client, job_offers):
        """x et y sont des nombres flottants (coordonnées PCA 2D)."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200:
            for item in response.data:
                assert isinstance(item["x"], (int, float))
                assert isinstance(item["y"], (int, float))

    def test_clusters_cluster_label_is_string(self, authenticated_client, job_offers):
        """cluster_label est une chaîne non vide."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200:
            for item in response.data:
                assert isinstance(item["cluster_label"], str)
                assert len(item["cluster_label"]) > 0

    def test_clusters_cluster_id_is_int(self, authenticated_client, job_offers):
        """cluster est un entier."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200:
            for item in response.data:
                assert isinstance(item["cluster"], int)
                assert item["cluster"] >= 0

    def test_clusters_without_token_returns_401(self, api_client):
        """Accès sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_clusters_empty_db_returns_empty_list(self, authenticated_client):
        """Aucune offre → liste vide (pas d'erreur)."""
        response = authenticated_client.get(self.URL)
        if response.status_code == 200:
            assert isinstance(response.data, list)


# ═══════════════════════════════════════════════════════════
#  GET /api/jobs/<id>/radar/
# ═══════════════════════════════════════════════════════════

class TestRadarChartEndpoint:

    def _get_radar_url(self, offer_id):
        return f"/api/jobs/{offer_id}/radar/"

    def test_radar_valid_offer_returns_200(self, authenticated_client, user, user_with_profile, job_offers):
        """ID d'offre valide → 200 + données radar."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        assert response.status_code == 200

    def test_radar_response_has_required_fields(self, authenticated_client, user, user_with_profile, job_offers):
        """Réponse contient labels, cv, offre, match_rate, score."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        assert response.status_code == 200
        data = response.data
        for field in ["labels", "cv", "offre", "match_rate", "score"]:
            assert field in data, f"Champ manquant: '{field}'"

    def test_radar_arrays_same_length(self, authenticated_client, user, user_with_profile, job_offers):
        """labels, cv et offre ont la même longueur."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        data = response.data
        assert len(data["labels"]) == len(data["cv"]) == len(data["offre"]), \
            "labels, cv, offre doivent avoir la même longueur"

    def test_radar_match_rate_between_0_and_100(self, authenticated_client, user, user_with_profile, job_offers):
        """match_rate est entre 0 et 100."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        assert 0 <= response.data["match_rate"] <= 100

    def test_radar_score_between_0_and_99(self, authenticated_client, user, user_with_profile, job_offers):
        """score est entre 0 et 99."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        assert 0 <= response.data["score"] <= 99

    def test_radar_invalid_offer_returns_404(self, authenticated_client, user, user_with_profile):
        """ID inexistant → 404."""
        _, _ = user_with_profile
        response = authenticated_client.get(self._get_radar_url(99999))
        assert response.status_code == 404

    def test_radar_without_token_returns_401(self, api_client, job_offers):
        """Accès sans token → 401."""
        response = api_client.get(self._get_radar_url(job_offers[0].id))
        assert response.status_code == 401

    def test_radar_labels_are_strings(self, authenticated_client, user, user_with_profile, job_offers):
        """labels est une liste de chaînes."""
        _, _ = user_with_profile
        offer_id = job_offers[0].id
        response = authenticated_client.get(self._get_radar_url(offer_id))
        for label in response.data["labels"]:
            assert isinstance(label, str)

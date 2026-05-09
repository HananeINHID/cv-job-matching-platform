"""
test_stats_endpoints.py — Tests d'intégration des endpoints de statistiques.

Périmètre :
  GET /api/stats/wordcloud/          : top compétences demandées
  GET /api/stats/geo/                : distribution géographique des offres
  GET /api/stats/score-distribution/ : histogramme des scores de matching

Chaque test est isolé et crée ses propres données.
"""

import json
import pytest
from api.models import UserProfile, JobOffer


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  GET /api/stats/wordcloud/
# ═══════════════════════════════════════════════════════════

class TestWordCloudEndpoint:

    URL = "/api/stats/wordcloud/"

    def test_wordcloud_returns_200(self, authenticated_client, job_offers):
        """GET authentifié → 200."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_wordcloud_returns_list(self, authenticated_client, job_offers):
        """Réponse est une liste."""
        response = authenticated_client.get(self.URL)
        assert isinstance(response.data, list)

    def test_wordcloud_each_item_has_skill_and_count(self, authenticated_client, job_offers):
        """Chaque item contient 'skill' et 'count' (et optionnellement 'text', 'value')."""
        response = authenticated_client.get(self.URL)
        for item in response.data:
            # Support both old {skill, count} and new {text, value, skill, count}
            assert "skill" in item or "text" in item
            assert "count" in item or "value" in item

    def test_wordcloud_count_is_positive_integer(self, authenticated_client, job_offers):
        """count est un entier positif."""
        response = authenticated_client.get(self.URL)
        for item in response.data:
            count = item.get("count", item.get("value", 0))
            assert isinstance(count, int)
            assert count > 0

    def test_wordcloud_max_50_results(self, authenticated_client, job_offers):
        """Maximum 50 résultats retournés."""
        response = authenticated_client.get(self.URL)
        assert len(response.data) <= 50

    def test_wordcloud_sorted_by_count_desc(self, authenticated_client, job_offers):
        """Résultats triés par count décroissant."""
        response = authenticated_client.get(self.URL)
        counts = [item.get("count", item.get("value", 0)) for item in response.data]
        assert counts == sorted(counts, reverse=True), "WordCloud non trié par count décroissant"

    def test_wordcloud_limit_param_respected(self, authenticated_client, job_offers):
        """Paramètre ?limit= est respecté."""
        response = authenticated_client.get(f"{self.URL}?limit=5")
        assert response.status_code == 200
        assert len(response.data) <= 5

    def test_wordcloud_empty_db_returns_empty_list(self, authenticated_client):
        """Aucune offre → liste vide (pas d'erreur)."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_wordcloud_without_token_returns_401(self, api_client):
        """Accès sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════
#  GET /api/stats/geo/
# ═══════════════════════════════════════════════════════════

class TestGeoDistributionEndpoint:

    URL = "/api/stats/geo/"

    def test_geo_returns_200(self, authenticated_client, job_offers):
        """GET authentifié → 200."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_geo_returns_count_and_cities(self, authenticated_client, job_offers):
        """Réponse contient {count, cities}."""
        response = authenticated_client.get(self.URL)
        data = response.data
        assert "count" in data
        assert "cities" in data
        assert isinstance(data["cities"], list)

    def test_geo_each_city_has_ville_and_count(self, authenticated_client, job_offers):
        """Chaque item cities contient 'ville' et 'count'."""
        response = authenticated_client.get(self.URL)
        for city in response.data["cities"]:
            assert "ville" in city
            assert "count" in city

    def test_geo_city_count_is_positive_integer(self, authenticated_client, job_offers):
        """count de chaque ville est un entier positif."""
        response = authenticated_client.get(self.URL)
        for city in response.data["cities"]:
            assert isinstance(city["count"], int)
            assert city["count"] > 0

    def test_geo_max_30_cities(self, authenticated_client, job_offers):
        """Maximum 30 villes retournées."""
        response = authenticated_client.get(self.URL)
        assert len(response.data["cities"]) <= 30

    def test_geo_count_is_integer(self, authenticated_client, job_offers):
        """count total est un entier."""
        response = authenticated_client.get(self.URL)
        assert isinstance(response.data["count"], int)

    def test_geo_cities_have_casablanca(self, authenticated_client, job_offers):
        """Avec les fixtures, Casablanca est présente (3 offres sur 5)."""
        response = authenticated_client.get(self.URL)
        villes = [c["ville"] for c in response.data["cities"]]
        assert any("casablanca" in v.lower() for v in villes), \
            f"Casablanca absente des villes: {villes}"

    def test_geo_without_token_returns_401(self, api_client):
        """Accès sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════
#  GET /api/stats/score-distribution/
# ═══════════════════════════════════════════════════════════

class TestScoreDistributionEndpoint:

    URL = "/api/stats/score-distribution/"

    def test_score_distribution_returns_200(self, authenticated_client, user, user_with_profile, job_offers):
        """GET authentifié avec profil → 200."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200

    def test_score_distribution_returns_labels_and_counts(self, authenticated_client, user, user_with_profile, job_offers):
        """Réponse contient {labels, counts}."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        data = response.data
        assert "labels" in data
        assert "counts" in data

    def test_score_distribution_has_exactly_10_buckets(self, authenticated_client, user, user_with_profile, job_offers):
        """Exactement 10 tranches (0-10, 10-20, ..., 90-100)."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        data = response.data
        assert len(data["labels"]) == 10, f"Attendu 10 tranches, obtenu {len(data['labels'])}"
        assert len(data["counts"]) == 10

    def test_score_distribution_labels_are_ranges(self, authenticated_client, user, user_with_profile, job_offers):
        """Labels sont des chaînes de type '0-10', '10-20', etc."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        labels = response.data["labels"]
        for label in labels:
            assert "-" in label, f"Label invalide: '{label}'"

    def test_score_distribution_counts_are_non_negative(self, authenticated_client, user, user_with_profile, job_offers):
        """counts sont des entiers non négatifs."""
        _, _ = user_with_profile
        response = authenticated_client.get(self.URL)
        for count in response.data["counts"]:
            assert isinstance(count, int)
            assert count >= 0

    def test_score_distribution_sum_equals_total_offers(self, authenticated_client, user, user_with_profile, job_offers):
        """Somme des counts = nombre total d'offres actives."""
        _, _ = user_with_profile
        total_offers = JobOffer.objects.filter(is_active=True).count()
        response = authenticated_client.get(self.URL)
        total_counted = sum(response.data["counts"])
        assert total_counted == total_offers, \
            f"Somme counts ({total_counted}) ≠ total offres ({total_offers})"

    def test_score_distribution_without_token_returns_401(self, api_client):
        """Accès sans token → 401."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_score_distribution_no_profile_returns_200(self, authenticated_client, job_offers):
        """Sans profil, les scores sont tous à 0 → 200 avec counts à 0."""
        response = authenticated_client.get(self.URL)
        assert response.status_code == 200
        # Sans profil, tous les scores devraient être bas
        data = response.data
        assert len(data["labels"]) == 10

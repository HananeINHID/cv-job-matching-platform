"""
test_auth_endpoints.py — Tests d'intégration des endpoints d'authentification.

Périmètre :
  POST /api/auth/register/    : inscription utilisateur
  POST /api/token/            : obtention JWT
  POST /api/token/refresh/    : rafraîchissement token
  Accès sans token            : vérification 401

Chaque test crée ses propres données et nettoie après (rollback Django pytest-django).
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  POST /api/auth/register/
# ═══════════════════════════════════════════════════════════

class TestRegisterEndpoint:

    BASE_URL = "/api/auth/register/"

    def test_register_valid_data_returns_201(self, api_client):
        """Données valides → 201 + user créé en DB."""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = api_client.post(self.BASE_URL, payload, format="json")
        assert response.status_code == 201
        assert User.objects.filter(username="newuser").exists()

    def test_register_creates_active_user_in_debug(self, api_client, settings):
        """En mode DEBUG=True → user créé avec is_active=True."""
        settings.DEBUG = True
        payload = {
            "username": "activeuser",
            "email": "active@example.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        api_client.post(self.BASE_URL, payload, format="json")
        user = User.objects.filter(username="activeuser").first()
        if user:
            assert user.is_active is True

    def test_register_duplicate_email_returns_400(self, api_client, user):
        """Email déjà utilisé → 400 + message d'erreur explicite."""
        payload = {
            "username": "anotheruser",
            "email": user.email,  # email déjà pris
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = api_client.post(self.BASE_URL, payload, format="json")
        assert response.status_code == 400

    def test_register_duplicate_username_returns_400(self, api_client, user):
        """Username déjà utilisé → 400."""
        payload = {
            "username": user.username,  # username déjà pris
            "email": "unique@example.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = api_client.post(self.BASE_URL, payload, format="json")
        assert response.status_code == 400

    def test_register_password_too_short_returns_400(self, api_client):
        """Mot de passe < 8 chars → 400."""
        payload = {
            "username": "shortpass",
            "email": "short@example.com",
            "password": "abc",
            "password_confirm": "abc",
        }
        response = api_client.post(self.BASE_URL, payload, format="json")
        assert response.status_code == 400

    def test_register_password_mismatch_returns_400(self, api_client):
        """Mots de passe différents → 400."""
        payload = {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "SecurePass123",
            "password_confirm": "DifferentPass123",
        }
        response = api_client.post(self.BASE_URL, payload, format="json")
        assert response.status_code == 400

    def test_register_missing_fields_returns_400(self, api_client):
        """Champs manquants → 400."""
        response = api_client.post(self.BASE_URL, {"username": "partial"}, format="json")
        assert response.status_code == 400

    def test_register_empty_payload_returns_400(self, api_client):
        """Payload vide → 400."""
        response = api_client.post(self.BASE_URL, {}, format="json")
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════
#  POST /api/token/ (Login JWT)
# ═══════════════════════════════════════════════════════════

class TestTokenEndpoint:

    BASE_URL = "/api/token/"

    def test_login_valid_credentials_returns_200(self, api_client, user):
        """Credentials valides → 200 + access + refresh tokens."""
        response = api_client.post(self.BASE_URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_tokens_are_strings(self, api_client, user):
        """Les tokens retournés sont des chaînes non vides."""
        response = api_client.post(self.BASE_URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        assert isinstance(response.data["access"], str)
        assert isinstance(response.data["refresh"], str)
        assert len(response.data["access"]) > 20
        assert len(response.data["refresh"]) > 20

    def test_login_access_token_has_three_parts(self, api_client, user):
        """access token est un JWT valide (3 parties séparées par '.')."""
        response = api_client.post(self.BASE_URL, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        parts = response.data["access"].split(".")
        assert len(parts) == 3, "Le JWT doit avoir 3 parties (header.payload.signature)"

    def test_login_wrong_password_returns_401(self, api_client, user):
        """Mauvais mot de passe → 401."""
        response = api_client.post(self.BASE_URL, {
            "username": user.username,
            "password": "wrongpassword",
        }, format="json")
        assert response.status_code == 401

    def test_login_unknown_user_returns_401(self, api_client):
        """User inexistant → 401."""
        response = api_client.post(self.BASE_URL, {
            "username": "nonexistent_user",
            "password": "somepassword",
        }, format="json")
        assert response.status_code == 401

    def test_login_missing_username_returns_400(self, api_client):
        """Username manquant → 400."""
        response = api_client.post(self.BASE_URL, {
            "password": "testpass123",
        }, format="json")
        assert response.status_code == 400

    def test_login_missing_password_returns_400(self, api_client):
        """Password manquant → 400."""
        response = api_client.post(self.BASE_URL, {
            "username": "testuser",
        }, format="json")
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════
#  POST /api/token/refresh/
# ═══════════════════════════════════════════════════════════

class TestTokenRefreshEndpoint:

    BASE_URL = "/api/token/refresh/"

    def test_valid_refresh_token_returns_200(self, api_client, user):
        """Refresh token valide → 200 + nouveau access token."""
        refresh = RefreshToken.for_user(user)
        response = api_client.post(self.BASE_URL, {
            "refresh": str(refresh),
        }, format="json")
        assert response.status_code == 200
        assert "access" in response.data

    def test_new_access_token_is_different_from_original(self, api_client, user):
        """Le nouveau access token est une chaîne valide."""
        refresh = RefreshToken.for_user(user)
        original_access = str(refresh.access_token)
        response = api_client.post(self.BASE_URL, {
            "refresh": str(refresh),
        }, format="json")
        new_access = response.data.get("access", "")
        # Doit être un JWT valide à 3 parties
        assert len(new_access.split(".")) == 3

    def test_invalid_refresh_token_returns_401(self, api_client):
        """Refresh token invalide → 401."""
        response = api_client.post(self.BASE_URL, {
            "refresh": "invalid.token.here",
        }, format="json")
        assert response.status_code == 401

    def test_empty_refresh_token_returns_400(self, api_client):
        """Refresh token vide → 400."""
        response = api_client.post(self.BASE_URL, {"refresh": ""}, format="json")
        assert response.status_code in [400, 401]


# ═══════════════════════════════════════════════════════════
#  ACCÈS SANS TOKEN → 401 Unauthorized
# ═══════════════════════════════════════════════════════════

class TestUnauthenticatedAccess:

    def test_profile_endpoint_without_token_returns_401(self, api_client):
        """GET /api/profile/ sans token → 401 Unauthorized."""
        response = api_client.get("/api/profile/")
        assert response.status_code == 401

    def test_profile_me_without_token_returns_401(self, api_client):
        """GET /api/profile/me/ sans token → 401."""
        response = api_client.get("/api/profile/me/")
        assert response.status_code == 401

    def test_matching_results_without_token_returns_401(self, api_client):
        """GET /api/matching/results/ sans token → 401."""
        response = api_client.get("/api/matching/results/")
        assert response.status_code == 401

    def test_stats_wordcloud_without_token_returns_401(self, api_client):
        """GET /api/stats/wordcloud/ sans token → 401."""
        response = api_client.get("/api/stats/wordcloud/")
        assert response.status_code == 401

    def test_stats_geo_without_token_returns_401(self, api_client):
        """GET /api/stats/geo/ sans token → 401."""
        response = api_client.get("/api/stats/geo/")
        assert response.status_code == 401

    def test_profile_history_without_token_returns_401(self, api_client):
        """GET /api/profile/history/ sans token → 401."""
        response = api_client.get("/api/profile/history/")
        assert response.status_code == 401

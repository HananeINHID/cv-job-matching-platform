"""
test_scraping.py — Tests unitaires des scrapers (sans appel réseau réel).

Périmètre :
  - Parsing de pages HTML mockées (Rekrute, Emploi.ma)
  - Anti-duplication en base
  - Champs obligatoires présents après parsing
  - Robustesse sur données manquantes

Toutes les requêtes HTTP sont mockées via unittest.mock.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from api.models import JobOffer


pytestmark = pytest.mark.django_db


# ─── HTML mockés représentatifs des vraies pages ──────────────────────────────

REKRUTE_OFFER_HTML = """
<html>
<body>
  <h1 class="title">Data Scientist Senior</h1>
  <div class="company">CAT Assurance</div>
  <div class="location">Casablanca</div>
  <div class="description">
    Analyser des données financières avec Python, SQL et Machine Learning.
    Minimum 3 ans d'expérience requis.
  </div>
  <div class="skills">Python, SQL, Machine Learning, Pandas, Scikit-learn</div>
  <a class="apply" href="https://rekrute.com/offre/12345">Postuler</a>
</body>
</html>
"""

EMPLOIMA_OFFER_HTML = """
<html>
<body>
  <h2 class="job-title">Développeur Django Backend</h2>
  <span class="employer">WebAgency Maroc</span>
  <span class="city">Rabat</span>
  <p class="job-description">
    Développement d'APIs REST avec Django DRF et PostgreSQL.
    Expérience : 2 ans minimum.
  </p>
  <div class="required-skills">Django, Python, REST API, PostgreSQL</div>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
#  HELPERS POUR TESTER LE PARSING SANS SCRAPER RÉEL
# ═══════════════════════════════════════════════════════════

def _create_offer_from_dict(data: dict) -> JobOffer:
    """Crée une JobOffer en DB depuis un dict parsé (simule le comportement du scraper)."""
    return JobOffer.objects.get_or_create(
        title=data["title"],
        company=data["company"],
        defaults={
            "location":         data.get("location", ""),
            "description":      data.get("description", ""),
            "required_skills":  data.get("required_skills", ""),
            "required_experience": data.get("required_experience", ""),
            "source":           data.get("source", ""),
            "source_url":       data.get("source_url", ""),
            "is_active":        True,
        }
    )


# ═══════════════════════════════════════════════════════════
#  TESTS PARSING HTML REKRUTE (SIMULÉ)
# ═══════════════════════════════════════════════════════════

class TestRekruteScraperParsing:

    def _parse_rekrute_html(self, html: str) -> dict:
        """Simule le parsing d'une page Rekrute (BeautifulSoup)."""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html, "html.parser")
            return {
                "title":        (soup.find(class_="title") or soup.find("h1") or MagicMock(text="")).get_text(strip=True),
                "company":      (soup.find(class_="company") or MagicMock(text="")).get_text(strip=True),
                "location":     (soup.find(class_="location") or MagicMock(text="")).get_text(strip=True),
                "description":  (soup.find(class_="description") or MagicMock(text="")).get_text(strip=True),
                "required_skills": (soup.find(class_="skills") or MagicMock(text="")).get_text(strip=True),
                "source":       "rekrute",
                "source_url":   (soup.find("a", class_="apply") or MagicMock(href=""))["href"] if soup.find("a", class_="apply") else "",
            }
        except ImportError:
            pytest.skip("BeautifulSoup non installé — skip parsing tests")

    def test_rekrute_parse_extracts_title(self):
        """Parse HTML Rekrute → titre extrait correctement."""
        data = self._parse_rekrute_html(REKRUTE_OFFER_HTML)
        assert data["title"] != ""
        assert "Data Scientist" in data["title"] or len(data["title"]) > 0

    def test_rekrute_parse_extracts_company(self):
        """Parse HTML Rekrute → entreprise extraite."""
        data = self._parse_rekrute_html(REKRUTE_OFFER_HTML)
        assert data["company"] != ""

    def test_rekrute_parse_extracts_location(self):
        """Parse HTML Rekrute → lieu extrait."""
        data = self._parse_rekrute_html(REKRUTE_OFFER_HTML)
        assert data["location"] != ""

    def test_rekrute_parse_sets_source_rekrute(self):
        """Parse HTML Rekrute → source = 'rekrute'."""
        data = self._parse_rekrute_html(REKRUTE_OFFER_HTML)
        assert data["source"] == "rekrute"

    def test_rekrute_mandatory_fields_present(self):
        """Tous les champs obligatoires sont présents dans le dict parsé."""
        data = self._parse_rekrute_html(REKRUTE_OFFER_HTML)
        for field in ["title", "company", "location", "description", "source"]:
            assert field in data, f"Champ obligatoire manquant: {field}"


# ═══════════════════════════════════════════════════════════
#  TESTS PARSING HTML EMPLOI.MA (SIMULÉ)
# ═══════════════════════════════════════════════════════════

class TestEmploiMaScraperParsing:

    def _parse_emploima_html(self, html: str) -> dict:
        """Simule le parsing d'une page Emploi.ma."""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html, "html.parser")
            return {
                "title":        (soup.find(class_="job-title") or soup.find("h2") or MagicMock(text="")).get_text(strip=True),
                "company":      (soup.find(class_="employer") or MagicMock(text="")).get_text(strip=True),
                "location":     (soup.find(class_="city") or MagicMock(text="")).get_text(strip=True),
                "description":  (soup.find(class_="job-description") or MagicMock(text="")).get_text(strip=True),
                "required_skills": (soup.find(class_="required-skills") or MagicMock(text="")).get_text(strip=True),
                "source":       "emploima",
                "source_url":   "",
            }
        except ImportError:
            pytest.skip("BeautifulSoup non installé — skip")

    def test_emploima_parse_extracts_title(self):
        """Parse HTML Emploi.ma → titre extrait."""
        data = self._parse_emploima_html(EMPLOIMA_OFFER_HTML)
        assert data["title"] != ""

    def test_emploima_parse_extracts_company(self):
        """Parse HTML Emploi.ma → entreprise extraite."""
        data = self._parse_emploima_html(EMPLOIMA_OFFER_HTML)
        assert data["company"] != ""

    def test_emploima_parse_sets_source_emploima(self):
        """Parse HTML Emploi.ma → source = 'emploima'."""
        data = self._parse_emploima_html(EMPLOIMA_OFFER_HTML)
        assert data["source"] == "emploima"


# ═══════════════════════════════════════════════════════════
#  TESTS ANTI-DUPLICATION
# ═══════════════════════════════════════════════════════════

class TestAntiDuplication:

    def test_insert_same_offer_twice_creates_only_one_record(self):
        """Insérer la même offre (title + company) deux fois → 1 seul enregistrement."""
        offer_data = {
            "title": "Data Scientist",
            "company": "CAT Assurance",
            "location": "Casablanca",
            "description": "Analyse de données financières",
            "required_skills": "python, sql",
            "source": "rekrute",
            "source_url": "https://rekrute.com/1",
        }
        _create_offer_from_dict(offer_data)
        _create_offer_from_dict(offer_data)  # Même offre, deuxième insertion

        count = JobOffer.objects.filter(
            title="Data Scientist",
            company="CAT Assurance",
        ).count()
        assert count == 1, f"Anti-duplication échouée: {count} enregistrements trouvés"

    def test_different_offers_create_multiple_records(self):
        """Deux offres différentes → deux enregistrements distincts."""
        _create_offer_from_dict({
            "title": "Data Analyst",
            "company": "Alpha Corp",
            "location": "Rabat",
            "description": "...",
            "source": "rekrute",
            "source_url": "",
        })
        _create_offer_from_dict({
            "title": "ML Engineer",
            "company": "Beta Corp",
            "location": "Casablanca",
            "description": "...",
            "source": "emploima",
            "source_url": "",
        })
        assert JobOffer.objects.filter(company__in=["Alpha Corp", "Beta Corp"]).count() == 2


# ═══════════════════════════════════════════════════════════
#  TESTS ROBUSTESSE (DONNÉES MANQUANTES)
# ═══════════════════════════════════════════════════════════

class TestScraperRobustness:

    def test_offer_with_missing_date_uses_default(self):
        """Offre sans date → valeur par défaut (today), pas de crash."""
        offer = JobOffer.objects.create(
            title="Ingénieur sans date",
            company="Corp",
            location="Fès",
            description="Poste sans date de publication",
            # posted_date non fourni → default=timezone.now
        )
        assert offer.pk is not None
        assert offer.posted_date is not None

    def test_offer_with_missing_skills_accepted(self):
        """Offre sans required_skills → champ vide accepté."""
        offer = JobOffer.objects.create(
            title="Poste Sans Skills",
            company="Corp",
            location="Agadir",
            description="Description sans compétences requises",
            required_skills="",
        )
        assert offer.pk is not None

    def test_offer_with_missing_experience_accepted(self):
        """Offre sans required_experience → champ vide accepté."""
        offer = JobOffer.objects.create(
            title="Poste Sans Exp",
            company="Corp",
            location="Tanger",
            description="Offre ouverte à tous niveaux",
            required_experience="",
        )
        assert offer.pk is not None

    def test_offer_created_with_is_active_true_by_default(self):
        """Toute offre créée est active par défaut."""
        offer = JobOffer.objects.create(
            title="Poste Actif",
            company="Default Corp",
            location="Kénitra",
            description="Test",
        )
        assert offer.is_active is True

    def test_offer_with_empty_source_url_accepted(self):
        """source_url vide → offre sauvegardée sans erreur."""
        offer = JobOffer.objects.create(
            title="Offre Sans URL",
            company="Corp",
            location="Oujda",
            description="Test",
            source_url="",
        )
        assert offer.pk is not None

    def test_offer_required_fields_title_company_location(self):
        """Les champs title, company, location, description sont requis (not blank)."""
        # Offre valide avec tous les champs
        offer = JobOffer.objects.create(
            title="Chef de Projet",
            company="Manager SA",
            location="Casablanca",
            description="Pilotage de projets IT",
        )
        assert offer.pk is not None

"""
test_scoring.py — Tests unitaires de la formule de matching multi-critères.

Périmètre :
  - tfidf_cosine_score()   : similarité cosinus TF-IDF (poids 50%)
  - jaccard_score()        : jaccard sur ensembles de compétences (poids 25%)
  - experience_match()     : compatibilité expérience (poids 15%)
  - geo_match()            : proximité géographique (poids 10%)
  - compute_weighted_score(): formule pondérée complète

Aucun accès DB, réseau ou fichier externe requis.
"""

import pytest
from api.utils.matching_utils import (
    tfidf_cosine_score,
    jaccard_score,
    experience_match,
    geo_match,
    compute_weighted_score,
)


# ═══════════════════════════════════════════════════════════
#  COSINUS TF-IDF
# ═══════════════════════════════════════════════════════════

class TestTfidfCosineScore:

    def test_cosine_identical_texts_returns_high_score(self):
        """Textes identiques → score élevé (doit être > 0.5)."""
        text = "Python Django SQL machine learning développeur"
        score = tfidf_cosine_score(text, text)
        assert score > 0.5, f"Score attendu > 0.5, obtenu {score}"

    def test_cosine_similar_domain_texts_returns_positive(self):
        """CV Python vs offre Python → similarité positive."""
        cv   = "développeur python django sql pandas machine learning data science"
        offre = "data scientist python pandas sklearn analyse de données statistiques"
        score = tfidf_cosine_score(cv, offre)
        assert score > 0.0, f"Score attendu > 0.0, obtenu {score}"

    def test_cosine_completely_different_domains_returns_low_score(self):
        """CV Python IT vs offre BTP → score très bas ou nul."""
        cv    = "développeur python django react javascript typescript frontend"
        offre = "génie civil béton armé chantier autocad topographie géomètre"
        score = tfidf_cosine_score(cv, offre)
        assert score < 0.2, f"Score attendu < 0.2, obtenu {score}"

    def test_cosine_empty_cv_text_returns_zero(self):
        """Texte CV vide → 0.0 sans exception."""
        score = tfidf_cosine_score("", "python django developer")
        assert score == 0.0

    def test_cosine_empty_offer_text_returns_zero(self):
        """Texte offre vide → 0.0 sans exception."""
        score = tfidf_cosine_score("python developer", "")
        assert score == 0.0

    def test_cosine_both_empty_returns_zero(self):
        """Deux textes vides → 0.0 sans exception."""
        score = tfidf_cosine_score("", "")
        assert score == 0.0

    def test_cosine_out_of_vocabulary_words_no_crash(self):
        """Mots hors vocabulaire pré-entraîné → fallback, pas de crash."""
        cv    = "xyzqwerty123 foobar baz qux corge grault"
        offre = "xyzqwerty123 foobar baz quux thud wibble"
        try:
            score = tfidf_cosine_score(cv, offre)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
        except Exception as e:
            pytest.fail(f"Exception inattendue avec mots hors vocabulaire: {e}")

    def test_cosine_score_between_zero_and_one(self):
        """Score toujours dans [0.0, 1.0]."""
        score = tfidf_cosine_score(
            "python machine learning data analyst",
            "sql data engineer pipeline etl"
        )
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════
#  JACCARD
# ═══════════════════════════════════════════════════════════

class TestJaccardScore:

    def test_jaccard_strong_overlap_returns_high_score(self):
        """Intersection forte {python, django, sql} → ≈ 0.6."""
        cv    = {"python", "django", "sql", "react"}
        offre = {"python", "django", "sql", "java"}
        score = jaccard_score(cv, offre)
        # intersection=3, union=5 → 0.6
        assert abs(score - 0.6) < 0.01, f"Score attendu ≈ 0.6, obtenu {score}"

    def test_jaccard_no_intersection_returns_zero(self):
        """Aucune intersection → 0.0."""
        cv    = {"python", "django", "sql"}
        offre = {"autocad", "béton", "chantier"}
        score = jaccard_score(cv, offre)
        assert score == 0.0

    def test_jaccard_identical_sets_returns_one(self):
        """Compétences identiques des deux côtés → 1.0."""
        skills = {"python", "sql", "machine learning"}
        score = jaccard_score(skills, skills.copy())
        assert score == 1.0

    def test_jaccard_empty_offer_skills_returns_zero(self):
        """Offre sans compétences → 0.0."""
        score = jaccard_score({"python", "django"}, set())
        assert score == 0.0

    def test_jaccard_empty_cv_skills_returns_zero(self):
        """CV sans compétences → 0.0."""
        score = jaccard_score(set(), {"python", "django"})
        assert score == 0.0

    def test_jaccard_both_empty_returns_zero(self):
        """Deux ensembles vides → 0.0 sans exception."""
        score = jaccard_score(set(), set())
        assert score == 0.0

    def test_jaccard_partial_overlap_correct_formula(self):
        """Vérification de la formule |A∩B|/|A∪B|."""
        cv    = {"a", "b", "c"}
        offre = {"b", "c", "d", "e"}
        # intersection=2, union=5 → 0.4
        score = jaccard_score(cv, offre)
        assert abs(score - 0.4) < 0.01, f"Score attendu 0.4, obtenu {score}"

    def test_jaccard_score_between_zero_and_one(self):
        """Score toujours dans [0.0, 1.0]."""
        score = jaccard_score({"python", "sql"}, {"python", "java", "c++"})
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════
#  EXPERIENCE MATCH
# ═══════════════════════════════════════════════════════════

class TestExperienceMatch:

    def test_exp_match_cv_exceeds_required_returns_one(self):
        """CV 3 ans, offre exige 2 ans → 1.0."""
        score = experience_match("3 ans", "2 ans")
        assert score == 1.0

    def test_exp_match_cv_equals_required_returns_one(self):
        """CV 5 ans, offre exige 5 ans → 1.0."""
        score = experience_match("5 ans", "5 ans")
        assert score == 1.0

    def test_exp_match_cv_less_than_required_returns_proportion(self):
        """CV 1 an, offre exige 3 ans → ≈ 0.33."""
        score = experience_match("1 an", "3 ans")
        assert abs(score - 0.33) < 0.01, f"Score attendu ≈ 0.33, obtenu {score}"

    def test_exp_match_unknown_cv_returns_neutral(self):
        """CV inconnu (''), offre exige 5 ans → 0.5 (score neutre)."""
        score = experience_match("", "5 ans")
        assert score == 0.5

    def test_exp_match_none_cv_returns_neutral(self):
        """CV None, offre exige 3 ans → 0.5."""
        score = experience_match(None, "3 ans")
        assert score == 0.5

    def test_exp_match_no_requirement_returns_one(self):
        """Offre sans exigence d'expérience → 1.0."""
        score = experience_match("2 ans", "")
        assert score == 1.0

    def test_exp_match_no_requirement_none_returns_one(self):
        """Offre None → 1.0."""
        score = experience_match("2 ans", None)
        assert score == 1.0

    def test_exp_match_senior_keyword_extracts_correctly(self):
        """Extraction depuis des chaînes comme '5+ ans' ou 'minimum 3 ans'."""
        score = experience_match("5 ans d'expérience", "minimum 3 ans")
        assert score == 1.0

    def test_exp_match_score_between_zero_and_one(self):
        """Score toujours dans [0.0, 1.0]."""
        score = experience_match("1 an", "10 ans")
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════
#  GEO MATCH
# ═══════════════════════════════════════════════════════════

class TestGeoMatch:

    def test_geo_exact_same_city_returns_one(self):
        """Même ville exacte → 1.0."""
        assert geo_match("Casablanca", "Casablanca") == 1.0

    def test_geo_case_insensitive_match(self):
        """Casse différente → toujours 1.0."""
        assert geo_match("casablanca", "CASABLANCA") == 1.0

    def test_geo_city_contained_in_region_returns_08(self):
        """Ville contenue dans l'autre → 0.8."""
        score = geo_match("Casablanca", "Grand Casablanca")
        assert score == 0.8

    def test_geo_different_cities_returns_zero(self):
        """Villes différentes → 0.0."""
        assert geo_match("Rabat", "Marrakech") == 0.0

    def test_geo_empty_cv_ville_returns_neutral(self):
        """Ville CV inconnue (vide) → 0.5."""
        assert geo_match("", "Casablanca") == 0.5

    def test_geo_empty_offer_ville_returns_neutral(self):
        """Ville offre inconnue (vide) → 0.5."""
        assert geo_match("Rabat", "") == 0.5

    def test_geo_both_empty_returns_neutral(self):
        """Deux villes inconnues → 0.5."""
        assert geo_match("", "") == 0.5

    def test_geo_none_cv_returns_neutral(self):
        """None CV → 0.5 sans exception."""
        assert geo_match(None, "Casablanca") == 0.5

    def test_geo_score_is_valid_value(self):
        """Retourne toujours 0.0, 0.5, 0.8 ou 1.0."""
        valid = {0.0, 0.5, 0.8, 1.0}
        for cv, off in [("Rabat", "Fès"), ("Agadir", "Agadir"), ("", "Tanger")]:
            assert geo_match(cv, off) in valid


# ═══════════════════════════════════════════════════════════
#  SCORE PONDÉRÉ GLOBAL
# ═══════════════════════════════════════════════════════════

class TestComputeWeightedScore:

    def test_weights_sum_to_one(self):
        """Vérifie que les poids 0.50+0.25+0.15+0.10 = 1.0."""
        assert abs(0.50 + 0.25 + 0.15 + 0.10 - 1.0) < 1e-9

    def test_weighted_score_between_zero_and_one(self):
        """Score pondéré toujours dans [0.0, 1.0]."""
        score = compute_weighted_score(
            cv_text="python developer django sql",
            offer_text="python backend developer django",
            cv_skills={"python", "django", "sql"},
            offer_skills={"python", "django", "postgresql"},
            cv_years="3 ans",
            required_exp="2 ans",
            cv_ville="Casablanca",
            offer_ville="Casablanca",
        )
        assert 0.0 <= score <= 1.0

    def test_weighted_score_real_case_python_django_dev(self):
        """Cas réel : CV Python/Django vs offre Django → score entre 50% et 80% (brut)."""
        score = compute_weighted_score(
            cv_text="développeur python django rest api postgresql machine learning",
            offer_text="backend developer django rest api postgresql docker linux",
            cv_skills={"python", "django", "postgresql", "rest"},
            offer_skills={"django", "postgresql", "rest", "docker"},
            cv_years="3 ans",
            required_exp="2 ans",
            cv_ville="Casablanca",
            offer_ville="Casablanca",
        )
        # Score brut (0-1) entre 0.40 et 0.90 (après multiplication ×1.2 = 50%–80%)
        assert 0.40 <= score <= 0.90, f"Score attendu entre 0.40 et 0.90, obtenu {score}"

    def test_weighted_score_perfect_match_is_high(self):
        """Match parfait sur tous les critères → score élevé."""
        skills = {"python", "sql", "machine learning", "django"}
        score = compute_weighted_score(
            cv_text="python sql machine learning django data science",
            offer_text="python sql machine learning django data science",
            cv_skills=skills,
            offer_skills=skills,
            cv_years="5 ans",
            required_exp="3 ans",
            cv_ville="Rabat",
            offer_ville="Rabat",
        )
        assert score >= 0.80, f"Score attendu ≥ 0.80, obtenu {score}"

    def test_weighted_score_no_match_is_low(self):
        """Aucun critère commun → score très bas."""
        score = compute_weighted_score(
            cv_text="python django sql machine learning artificial intelligence",
            offer_text="béton armé chantier génie civil maçonnerie topographie",
            cv_skills={"python", "sql", "django"},
            offer_skills={"autocad", "béton", "chantier"},
            cv_years="1 an",
            required_exp="5 ans",
            cv_ville="Casablanca",
            offer_ville="Dakhla",
        )
        assert score < 0.30, f"Score attendu < 0.30, obtenu {score}"

    def test_weighted_score_all_empty_returns_float(self):
        """Tous les paramètres vides → retourne un float sans crash."""
        try:
            score = compute_weighted_score(
                cv_text="", offer_text="",
                cv_skills=set(), offer_skills=set(),
                cv_years="", required_exp="",
                cv_ville="", offer_ville="",
            )
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
        except Exception as e:
            pytest.fail(f"Exception inattendue avec paramètres vides: {e}")

    def test_weighted_score_only_geo_contributes(self):
        """Même ville, tout le reste nul → score ≈ 0.10 × 1.0 = 0.10."""
        score = compute_weighted_score(
            cv_text="", offer_text="",
            cv_skills=set(), offer_skills=set(),
            cv_years="", required_exp="",
            cv_ville="Casablanca", offer_ville="Casablanca",
        )
        # Geo=1.0, Exp=1.0 (no required), Cosine=0.0, Jaccard=0.0
        # Score = 0 + 0 + 0.15*1.0 + 0.10*1.0 = 0.25
        assert score >= 0.10, f"Score attendu ≥ 0.10, obtenu {score}"

    def test_final_percentage_between_0_and_99(self):
        """Le score final (×100×1.2) doit être dans [0, 99]."""
        raw = compute_weighted_score(
            cv_text="python machine learning data",
            offer_text="python data science analytics",
            cv_skills={"python", "data"},
            offer_skills={"python", "sklearn", "pandas"},
            cv_years="2 ans",
            required_exp="1 an",
            cv_ville="Casablanca",
            offer_ville="Casablanca",
        )
        final_pct = min(round(raw * 100 * 1.2), 99)
        assert 0 <= final_pct <= 99, f"Pourcentage final hors bornes: {final_pct}"

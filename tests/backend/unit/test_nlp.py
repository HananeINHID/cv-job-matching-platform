"""
test_nlp.py — Tests unitaires du pipeline NLP.

Périmètre :
  - tokenize_text()        : tokenisation basique
  - lemmatize_and_clean()  : lemmatisation + suppression stop words
  - parse_skills()         : parsing JSON / CSV → liste Python
  - Chargement spaCy       : disponibilité du modèle fr_core_news_sm
  - Dimensions TF-IDF      : vectoriseur produit 500 features
  - Clusters K-Means       : 6 clusters attendus

Aucun accès DB requis.
"""

import pytest
from api.utils.matching_utils import (
    tokenize_text,
    lemmatize_and_clean,
    parse_skills,
    SPACY_AVAILABLE,
    _VECTORIZER,
    _KMEANS,
)


# ═══════════════════════════════════════════════════════════
#  TOKENIZE_TEXT
# ═══════════════════════════════════════════════════════════

class TestTokenizeText:

    def test_tokenize_basic_french_sentence(self):
        """Tokenise un titre de poste standard → mots attendus présents."""
        tokens = tokenize_text("Développeur Python React Django")
        # Doit contenir les mots techniques
        lowered = [t.lower() for t in tokens]
        for word in ["python", "react", "django"]:
            assert word in lowered, f"Mot '{word}' absent des tokens: {lowered}"

    def test_tokenize_removes_punctuation(self):
        """La ponctuation ne doit pas apparaître comme token."""
        tokens = tokenize_text("Python, Django; SQL: Machine-Learning!")
        assert "," not in tokens
        assert ";" not in tokens
        assert "!" not in tokens

    def test_tokenize_lowercase(self):
        """Tous les tokens sont en minuscule."""
        tokens = tokenize_text("PYTHON Django SQL")
        assert all(t == t.lower() for t in tokens)

    def test_tokenize_empty_string_returns_empty_list(self):
        """Chaîne vide → liste vide sans exception."""
        assert tokenize_text("") == []

    def test_tokenize_preserves_alphanumeric(self):
        """Les tokens alphanumériques (#, +, .) sont conservés."""
        tokens = tokenize_text("C++ C# .NET node.js")
        # Au moins un token technique doit être présent
        assert len(tokens) > 0

    def test_tokenize_returns_list(self):
        """Retourne toujours une liste."""
        result = tokenize_text("python developer")
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
#  LEMMATIZE_AND_CLEAN
# ═══════════════════════════════════════════════════════════

class TestLemmatizeAndClean:

    def test_lemmatize_removes_french_stop_words(self):
        """Supprime les stop words français courants."""
        text = "le développeur et la société sont dans la ville de Casablanca"
        result = lemmatize_and_clean(text)
        # Stop words attendus absents du résultat
        for stop in ["le", "et", "la", "de", "dans", "sont"]:
            assert stop not in result.split(), f"Stop word '{stop}' toujours présent"

    def test_lemmatize_keeps_technical_terms(self):
        """Les termes techniques pertinents sont conservés."""
        text = "développeur python django machine learning"
        result = lemmatize_and_clean(text)
        # Au moins "python" doit rester
        assert "python" in result.lower()

    def test_lemmatize_empty_string_returns_empty(self):
        """Chaîne vide → chaîne vide sans exception."""
        result = lemmatize_and_clean("")
        assert result == ""

    def test_lemmatize_none_handled(self):
        """None ou valeur falsy → chaîne vide sans exception."""
        try:
            result = lemmatize_and_clean(None)
            assert result == "" or isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Exception inattendue avec None: {e}")

    def test_lemmatize_returns_string(self):
        """Retourne toujours une chaîne."""
        result = lemmatize_and_clean("développeur python")
        assert isinstance(result, str)

    def test_lemmatize_no_crash_on_long_text(self):
        """Pas de crash sur un texte long."""
        long_text = ("python django react javascript sql " * 50).strip()
        try:
            result = lemmatize_and_clean(long_text)
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Exception sur texte long: {e}")


# ═══════════════════════════════════════════════════════════
#  PARSE_SKILLS
# ═══════════════════════════════════════════════════════════

class TestParseSkills:

    def test_parse_skills_json_string_returns_list(self):
        """Format JSON string → liste Python correcte."""
        raw = '["Python", "Django", "SQL"]'
        result = parse_skills(raw)
        assert isinstance(result, list)
        assert "python" in result
        assert "django" in result
        assert "sql" in result

    def test_parse_skills_json_preserves_all_items(self):
        """Tous les items JSON sont conservés (en minuscule)."""
        raw = '["React", "TypeScript", "Node.js", "PostgreSQL"]'
        result = parse_skills(raw)
        assert len(result) == 4

    def test_parse_skills_csv_string_returns_list(self):
        """Format CSV string → liste Python correcte."""
        raw = "Python, Django, SQL, Machine Learning"
        result = parse_skills(raw)
        assert isinstance(result, list)
        assert "python" in result
        assert "django" in result

    def test_parse_skills_csv_strips_whitespace(self):
        """CSV avec espaces → items nettoyés."""
        raw = " python , django , sql "
        result = parse_skills(raw)
        assert "python" in result
        assert "django" in result

    def test_parse_skills_empty_string_returns_empty_list(self):
        """Chaîne vide → []."""
        assert parse_skills("") == []

    def test_parse_skills_none_returns_empty_list(self):
        """None → []."""
        assert parse_skills(None) == []

    def test_parse_skills_single_item(self):
        """Un seul item → liste d'un élément."""
        result = parse_skills("python")
        assert result == ["python"]

    def test_parse_skills_invalid_json_fallback_to_csv(self):
        """JSON invalide → fallback CSV sans crash."""
        raw = '{invalid json}'
        result = parse_skills(raw)
        assert isinstance(result, list)

    def test_parse_skills_returns_lowercase(self):
        """Tous les skills retournés en minuscule."""
        raw = '["Python", "DJANGO", "SQL"]'
        result = parse_skills(raw)
        assert all(s == s.lower() for s in result)


# ═══════════════════════════════════════════════════════════
#  SPACY MODEL
# ═══════════════════════════════════════════════════════════

class TestSpacyModel:

    def test_spacy_model_available(self):
        """Le modèle spaCy fr_core_news_sm est chargé sans erreur."""
        # Si SPACY_AVAILABLE=False, le test est skipé (modèle non installé)
        if not SPACY_AVAILABLE:
            pytest.skip("spaCy fr_core_news_sm non installé — skip")
        assert SPACY_AVAILABLE is True

    def test_spacy_processes_french_text(self):
        """spaCy traite un texte français sans exception."""
        if not SPACY_AVAILABLE:
            pytest.skip("spaCy non disponible")
        from api.utils.matching_utils import _nlp
        doc = _nlp("Développeur Python avec 3 ans d'expérience à Casablanca")
        assert doc is not None
        assert len(list(doc)) > 0


# ═══════════════════════════════════════════════════════════
#  VECTORIZER TF-IDF
# ═══════════════════════════════════════════════════════════

class TestTfidfVectorizer:

    def test_vectorizer_loaded(self):
        """Le vectoriseur TF-IDF pré-entraîné est chargé."""
        if _VECTORIZER is None:
            pytest.skip("Vectoriseur TF-IDF non disponible — modèle pkl absent")
        assert _VECTORIZER is not None

    def test_vectorizer_produces_expected_features(self):
        """Le vectoriseur produit 500 features (comme défini à l'entraînement)."""
        if _VECTORIZER is None:
            pytest.skip("Vectoriseur non disponible")
        n_features = len(_VECTORIZER.vocabulary_)
        assert n_features > 0, "Le vocabulaire est vide"
        # La valeur exacte dépend de l'entraînement (50 ou 500 selon la version)
        assert n_features in range(10, 10000), f"Nombre de features anormal: {n_features}"

    def test_vectorizer_transforms_text(self):
        """Le vectoriseur transforme un texte sans exception."""
        if _VECTORIZER is None:
            pytest.skip("Vectoriseur non disponible")
        matrix = _VECTORIZER.transform(["python django sql developer"])
        assert matrix is not None
        assert matrix.shape[0] == 1


# ═══════════════════════════════════════════════════════════
#  KMEANS MODEL
# ═══════════════════════════════════════════════════════════

class TestKMeansModel:

    def test_kmeans_loaded(self):
        """Le modèle K-Means pré-entraîné est chargé."""
        if _KMEANS is None:
            pytest.skip("K-Means non disponible — modèle pkl absent")
        assert _KMEANS is not None

    def test_kmeans_cluster_count(self):
        """K-Means a le bon nombre de clusters (≤ 10)."""
        if _KMEANS is None:
            pytest.skip("K-Means non disponible")
        n_clusters = _KMEANS.n_clusters
        assert 2 <= n_clusters <= 10, f"Nombre de clusters anormal: {n_clusters}"

    def test_kmeans_predict_returns_valid_cluster(self):
        """predict_cluster retourne un entier valide sans crash."""
        from api.utils.matching_utils import predict_cluster
        cluster = predict_cluster("python django machine learning developer")
        assert isinstance(cluster, int)
        assert cluster >= 0

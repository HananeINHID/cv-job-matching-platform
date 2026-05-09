"""
Utilitaires de matching CV ↔ offres d'emploi.

Fonctions pures (sans dépendances Django) utilisées par les views de matching.
Intègre : TF-IDF cosinus, Jaccard, expMatch, geoMatch, formule pondérée.
"""

import json
import re
import pickle
import os

# TF-IDF + cosinus (scikit-learn)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Chemins vers les modèles ML pré-entraînés
# __file__ = backend/api/utils/matching_utils.py
# 4x dirname => project root (parent of backend/)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
ML_MODELS_PATH = os.path.join(BASE_DIR, 'ml_models')

_VECTORIZER = None
_KMEANS = None

def _load_models():
    global _VECTORIZER, _KMEANS
    if _VECTORIZER is None:
        try:
            import warnings
            import sklearn
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # ignore sklearn version mismatch
                with open(os.path.join(ML_MODELS_PATH, 'vectorizer_tfidf.pkl'), 'rb') as f:
                    _VECTORIZER = pickle.load(f)
                with open(os.path.join(ML_MODELS_PATH, 'kmeans_model.pkl'), 'rb') as f:
                    _KMEANS = pickle.load(f)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"ML models non charges: {e}")

_load_models()

# spaCy 
try:
    import spacy
    _nlp = spacy.load("fr_core_news_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    _nlp = None
    SPACY_AVAILABLE = False

# Stop words français minimaliste (utilisé si spaCy absent)
_FR_STOP_WORDS = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "en",
    "au", "aux", "par", "pour", "sur", "dans", "avec", "est", "sont",
    "a", "à", "il", "elle", "nous", "vous", "ils", "que", "qui", "se",
    "ce", "ou", "mais", "donc", "or", "ni", "car", "si", "ne", "pas",
    "plus", "très", "bien", "tout", "même", "comme", "être", "avoir",
    "faire", "notre", "votre", "leur", "leurs", "an", "ans", "année",
}


#  NLP  tokenisation / lemmatisation

def tokenize_text(text: str) -> list[str]:
    """Tokenise un texte libre en mots minuscules (sans ponctuation)."""
    return re.findall(r'\b[a-zA-ZÀ-ÿ0-9#+.]+\b', text.lower())


def lemmatize_and_clean(text: str) -> str:
    """
    Lemmatise le texte et supprime les stop words.
    Utilise spaCy si disponible, sinon fallback regex + stop words FR.
    """
    if not text:
        return ""

    if SPACY_AVAILABLE and _nlp:
        doc = _nlp(text.lower())
        tokens = [
            t.lemma_ for t in doc
            if not t.is_stop and t.is_alpha and len(t.text) > 2
        ]
    else:
        tokens = [
            t for t in tokenize_text(text)
            if t not in _FR_STOP_WORDS and len(t) > 2
        ]

    return " ".join(tokens)


#  Skills - parsing

def parse_skills(raw: str) -> list[str]:
    """
    Convertit un champ skills (JSON ou CSV) en liste de tokens minuscules.
    Tolère JSON invalide, None et chaînes vides.
    """
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [s.strip().lower() for s in parsed if s.strip()]
    except (json.JSONDecodeError, TypeError):
        pass
    return [s.strip().lower() for s in raw.split(',') if s.strip()]


#  Scores de similarité

def tfidf_cosine_score(text_cv: str, text_offer: str) -> float:
    """
    Similarite cosinus TF-IDF entre deux textes (0.0 -> 1.0).
    Utilise le vectoriseur pre-entraine si disponible.
    Fallback automatique si le vocabulaire pre-entraine ne couvre pas les textes.
    """
    import numpy as np
    t1 = lemmatize_and_clean(text_cv)
    t2 = lemmatize_and_clean(text_offer)

    if not t1 or not t2:
        return 0.0

    try:
        if _VECTORIZER:
            matrix = _VECTORIZER.transform([t1, t2])
            # Si les deux vecteurs sont nuls (mots absents du vocabulaire pre-entraine),
            # basculer sur un vectoriseur a la volee pour ne pas retourner 0 injustement.
            norms = np.asarray(matrix.sum(axis=1)).flatten()
            if norms[0] == 0 or norms[1] == 0:
                raise ValueError("Vectors hors vocabulaire – fallback")
            score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            return float(score)
    except Exception:
        pass

    # Fallback : vectoriseur a la volee sur les deux textes uniquement
    try:
        v = TfidfVectorizer()
        matrix = v.fit_transform([t1, t2])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(score)
    except Exception:
        return 0.0

def predict_cluster(text: str) -> int:
    """
    Predit le cluster d'une offre d'emploi (utilise le modele K-Means).
    Applique une reduction PCA si le nombre de features est incompatible.
    """
    if not _VECTORIZER or not _KMEANS:
        return 0
    try:
        clean = lemmatize_and_clean(text)
        vector = _VECTORIZER.transform([clean])
        expected = getattr(_KMEANS, 'n_features_in_', None)
        if expected and vector.shape[1] != expected:
            # Le KMeans a ete entraine avec PCA(n_components=50) – reproduire
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=expected, random_state=42)
            vector = svd.fit_transform(vector)
        return int(_KMEANS.predict(vector)[0])
    except Exception:
        return 0


def jaccard_score(skills_cv: set, skills_offer: set) -> float:
    """
    Distance de Jaccard entre deux ensembles de compétences (0.0 → 1.0).
    """
    if not skills_cv or not skills_offer:
        return 0.0
    intersection = len(skills_cv & skills_offer)
    union = len(skills_cv | skills_offer)
    return intersection / union if union > 0 else 0.0


def experience_match(cv_years: str, required_exp: str) -> float:
    """
    Score de compatibilité expérience (0.0 → 1.0).
    Extrait le nombre d'années depuis des chaînes comme '3 ans', 'senior', etc.
    """
    def _extract_years(text: str) -> int | None:
        if not text:
            return None
        # Patterns numériques : "3 ans", "5+", "2-4 ans"
        m = re.search(r'(\d+)', str(text))
        return int(m.group(1)) if m else None

    req_y = _extract_years(required_exp)
    if req_y is None:
        return 1.0  # Pas d'exigence = match parfait

    cv_y = _extract_years(cv_years)
    if cv_y is None:
        return 0.5  # Expérience inconnue = score neutre

    if cv_y >= req_y:
        return 1.0
    return round(cv_y / req_y, 2)  # Score proportionnel


def geo_match(cv_ville: str, offer_ville: str) -> float:
    """
    Score de proximité géographique (0.0 → 1.0).
    1.0 = même ville, 0.8 = ville incluse dans l'autre, 0.0 = différent.
    """
    if not cv_ville or not offer_ville:
        return 0.5  # Inconnu = neutre

    cv_v = cv_ville.strip().lower()
    off_v = offer_ville.strip().lower()

    if cv_v == off_v:
        return 1.0
    if cv_v in off_v or off_v in cv_v:
        return 0.8
    return 0.0


#  Score pondéré final

def compute_weighted_score(
    cv_text: str,
    offer_text: str,
    cv_skills: set,
    offer_skills: set,
    cv_years: str = "",
    required_exp: str = "",
    cv_ville: str = "",
    offer_ville: str = "",
) -> float:
    """
    Score de compatibilité pondéré selon la formule du cahier des charges :
      Score = 0.50 * cosinusTFIDF
            + 0.25 * jaccardSkills
            + 0.15 * expMatch
            + 0.10 * geoMatch

    Retourne une valeur entre 0.0 et 1.0.
    """
    cosine = tfidf_cosine_score(cv_text, offer_text)
    jaccard = jaccard_score(cv_skills, offer_skills)
    exp = experience_match(cv_years, required_exp)
    geo = geo_match(cv_ville, offer_ville)

    return round(0.50 * cosine + 0.25 * jaccard + 0.15 * exp + 0.10 * geo, 4)

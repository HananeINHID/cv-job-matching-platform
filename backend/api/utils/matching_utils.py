"""
Utilitaires de matching CV ↔ offres d'emploi.

Fonctions pures (sans dépendances Django) utilisées par MatchingResultsView.
"""

import json
import math
import re


def parse_skills(raw: str) -> list[str]:
    """
    Convertit un champ skills (JSON ou CSV) en liste de tokens minuscules.
    Robuste : tolère JSON invalide, None, et chaînes vides.
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


def cosine_score(cv_tokens: list[str], offer_tokens: list[str]) -> float:
    """
    Score de similarité cosine (0.0 → 1.0) entre deux listes de tokens.
    Utilise un vecteur TF binaire (présence/absence).
    """
    if not cv_tokens or not offer_tokens:
        return 0.0

    vocab = set(cv_tokens) | set(offer_tokens)
    cv_set = set(cv_tokens)
    offer_set = set(offer_tokens)

    dot = sum(1 for w in vocab if w in cv_set and w in offer_set)
    norm_cv = math.sqrt(len(cv_set))
    norm_offer = math.sqrt(len(offer_set))

    if norm_cv == 0 or norm_offer == 0:
        return 0.0
    return dot / (norm_cv * norm_offer)


def tokenize_text(text: str) -> list[str]:
    """Tokenize un texte libre en mots minuscules (sans ponctuation)."""
    return re.findall(r'\b[a-zA-ZÀ-ÿ0-9#+.]+\b', text.lower())

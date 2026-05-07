"""
Views de matching CV ↔ offres d'emploi.

Endpoint: GET /api/matching/results/?q=<mot_clé_optionnel>  → MatchingResultsView
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile, JobOffer
from ..utils.matching_utils import parse_skills, cosine_score, tokenize_text


class MatchingResultsView(APIView):
    """
    Calcule et retourne les offres d'emploi triées par score de matching
    avec le profil CV de l'utilisateur connecté.

    Endpoint : GET /api/matching/results/?q=<mot_clé_optionnel>

    Algorithme :
      1. Charge le profil CV de l'utilisateur (hard_skills + titre)
      2. Pour chaque JobOffer active :
           - Extrait les required_skills + description
           - Calcule un score cosine skills  (poids 70 %)
           - Calcule un score cosine description (poids 30 %)
      3. Filtre optionnel ?q= sur titre ou ville de l'offre
      4. Retourne la liste triée par score décroissant

    Format de réponse :
    [
      {
        "id": 1,
        "titre": "Développeur React",
        "entreprise": "Capgemini",
        "ville": "Casablanca",
        "contrat": "CDI",
        "score": 87,
        "competences": ["React", "JavaScript"]
      },
      ...
    ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip().lower()

        # 1. Profil CV de l'utilisateur
        try:
            profile = UserProfile.objects.get(user=request.user)
            cv_skills = parse_skills(profile.hard_skills)
            cv_title_tokens = tokenize_text(profile.titre or '')
            cv_tokens = cv_skills + cv_title_tokens
        except UserProfile.DoesNotExist:
            cv_tokens = []

        # 2. Offres actives
        offres_qs = JobOffer.objects.filter(is_active=True)

        # Filtre optionnel sur le titre ou la ville
        if query:
            offres_qs = offres_qs.filter(
                title__icontains=query
            ) | JobOffer.objects.filter(
                is_active=True,
                location__icontains=query
            )

        # 3. Calcul des scores
        results = []
        for offre in offres_qs:
            offer_skills = parse_skills(offre.required_skills)
            offer_desc_tokens = tokenize_text(offre.description or '')

            if cv_tokens:
                score_skills = cosine_score(cv_tokens, offer_skills + tokenize_text(offre.title))
                score_desc = cosine_score(cv_tokens, offer_desc_tokens)
                # Pondération : skills 70 % + description 30 %
                raw_score = score_skills * 0.70 + score_desc * 0.30
            else:
                # Profil vide : score neutre basé sur la popularité
                raw_score = 0.5

            score_pct = round(min(raw_score * 100 * 1.5, 99))  # normalise vers 0-99

            # Compétences requises à afficher (max 6)
            competences_display = (
                [s.title() for s in offer_skills[:6]]
                if offer_skills
                else tokenize_text(offre.title)[:4]
            )

            results.append({
                "id": offre.id,
                "titre": offre.title,
                "entreprise": offre.company,
                "ville": offre.location,
                "contrat": offre.contract_type or "CDI",
                "score": score_pct,
                "competences": competences_display,
            })

        # 4. Tri par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)

        return Response(results, status=status.HTTP_200_OK)

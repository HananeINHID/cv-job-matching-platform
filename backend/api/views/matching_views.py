"""
Views de matching CV ↔ offres d'emploi.

Endpoint: GET /api/matching/results/?q=<mot_clé_optionnel>  → MatchingResultsView
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.management import call_command

from ..models import UserProfile, JobOffer, SearchHistory
from ..utils.matching_utils import (
    parse_skills,
    tokenize_text,
    compute_weighted_score,
)


def _build_cv_context(user):
    """Retourne le contexte CV complet de l'utilisateur."""
    try:
        profile = UserProfile.objects.prefetch_related(
            'experiences'
        ).get(user=user)

        # Texte CV = titre + hard skills + soft skills + résumé expériences
        exp_texts = " ".join([
            f"{e.poste or ''} {e.entreprise or ''} {e.description or ''}"
            for e in profile.experiences.all()
        ])
        cv_text = " ".join(filter(None, [
            profile.titre or '',
            profile.hard_skills or '',
            profile.soft_skills or '',
            exp_texts,
        ]))

        cv_skills = set(parse_skills(profile.hard_skills))
        cv_years = profile.experience_years or ''
        cv_ville = profile.ville or ''

        return cv_text, cv_skills, cv_years, cv_ville
    except UserProfile.DoesNotExist:
        return "", set(), "", ""


class MatchingResultsView(APIView):
    """
    Calcule et retourne les offres d'emploi triées par score de matching
    avec le profil CV de l'utilisateur connecté.

    Endpoint : GET /api/matching/results/?q=<mot_clé_optionnel>

    Algorithme (formule cahier des charges) :
      Score = 0.50 * cosinusTFIDF(CV, offre)
            + 0.25 * jaccard(skills CV, skills offre)
            + 0.15 * expMatch(années CV, exp requise)
            + 0.10 * geoMatch(ville CV, ville offre)

    Format de réponse :
    [
      {
        "id": 1,
        "titre": "Développeur React",
        "entreprise": "Capgemini",
        "ville": "Casablanca",
        "contrat": "CDI",
        "score": 87,
        "competences": ["React", "JavaScript"],
        "source": "rekrute",
        "source_url": "https://..."
      },
      ...
    ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip().lower()
        source = request.query_params.get('source', '').strip().lower()

        # 1. Contexte CV de l'utilisateur
        cv_text, cv_skills, cv_years, cv_ville = _build_cv_context(request.user)

        # 2. Offres actives (filtrées par source)
        offres_qs = JobOffer.objects.filter(is_active=True)
        if source and source != 'dataset':
            offres_qs = offres_qs.filter(source__iexact=source)

        # Tokenisation du mot-clé : "data analyste" → ["data","analyste"]
        # Permet de trouver "Data Analyst" même si l'utilisateur tape en français
        if query:
            tokens = [t for t in query.split() if len(t) > 2]
            if not tokens:
                tokens = [query]
            kw_q = Q()
            for token in tokens:
                kw_q |= Q(title__icontains=token)
                kw_q |= Q(description__icontains=token)
                kw_q |= Q(required_skills__icontains=token)
                kw_q |= Q(company__icontains=token)
                kw_q |= Q(sector__icontains=token)
                kw_q |= Q(location__icontains=token)
            # Recherche aussi sur le mot-clé complet (fallback)
            kw_q |= Q(title__icontains=query)
            kw_q |= Q(description__icontains=query)
            offres_qs = offres_qs.filter(kw_q).distinct()

        # 3. Calcul des scores
        results = []
        for offre in offres_qs:
            offer_text = " ".join(filter(None, [
                offre.title, offre.description, offre.required_skills
            ]))
            offer_skills = set(parse_skills(offre.required_skills))

            raw_score = compute_weighted_score(
                cv_text=cv_text,
                offer_text=offer_text,
                cv_skills=cv_skills,
                offer_skills=offer_skills,
                cv_years=cv_years,
                required_exp=offre.required_experience,
                cv_ville=cv_ville,
                offer_ville=offre.location,
            )

            score_pct = round(min(raw_score * 100 * 1.2, 99))

            competences_display = (
                [s.title() for s in list(offer_skills)[:6]]
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
                "source": offre.source,
                "source_url": offre.source_url,
            })

        # 4. Tri par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)

        # 5. Enregistrement dans l'historique (silencieux en cas d'erreur)
        try:
            SearchHistory.objects.create(
                user=request.user,
                keyword=query or source or 'dataset',
                source=source or 'dataset',
                results_count=len(results),
            )
        except Exception:
            pass

        return Response(results, status=status.HTTP_200_OK)


class ScrapeLinkedInView(APIView):
    """
    Lance le scraper LinkedIn pour un mot-clé spécifique de manière synchrone,
    pour que le frontend puisse afficher un loading jusqu'à la fin.
    POST /api/jobs/scrape/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        keyword = request.data.get('keyword', '')
        # On limite à 5 offres pour la recherche en temps réel et on force l'arrêt après un passage
        try:
            call_command('scrape_linkedin', keyword=keyword, limit=5, run_once=True)
            return Response({"status": "success", "message": "Scraping terminé."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

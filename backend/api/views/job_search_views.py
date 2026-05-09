"""
Views de recherche d'emplois.

Deux modes via le paramètre ?source= :
  - dataset                          → recherche dans les offres déjà en DB
  - rekrute | emploima | marocannonces → scraping temps réel (2 pages), sauvegarde en DB

Endpoint : GET /api/jobs/search/?q=<keyword>&source=<mode>&location=<lieu>
  - linkedin                         → scraping LinkedIn temps réel (Selenium Chrome)
"""

import os
import sys
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile, JobOffer, SearchHistory
from ..utils.matching_utils import parse_skills, tokenize_text, compute_weighted_score

logger = logging.getLogger(__name__)

REALTIME_PAGES = 2
VALID_SOURCES = {'rekrute', 'emploima', 'marocannonces', 'linkedin'}

# Chemin vers la racine du projet (parent de backend/)
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)


# ─────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────

def _get_scrapers():
    """
    Importe les classes de scraping depuis scraping/emploi.py.
    Lève ImportError si les dépendances ne sont pas installées.
    """
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    from scraping.emploi import RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper, LinkedInScraper
    return RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper, LinkedInScraper


def _fresh_progress(keyword: str) -> dict:
    """Crée un objet progress vierge (toujours partir de la page 1)."""
    return {
        "rekrute":       {keyword: 1},
        "emploima":      {keyword: 0},
        "marocannonces": {keyword: 1},
    }


def _save_scraped_offers(raw_offers: list, source_site: str) -> int:
    """
    Sauvegarde les offres scrapées en DB, ignore les doublons (titre + entreprise).
    Retourne le nombre de nouvelles offres insérées.
    """
    saved = 0
    for data in raw_offers:
        title = (data.get('title') or 'N/A')[:255]
        company = (data.get('company') or 'N/A')[:255]

        if JobOffer.objects.filter(title=title, company=company).exists():
            continue

        # Extraire l'URL depuis "NomSite | https://..."
        raw_source = data.get('source') or ''
        source_url = ''
        if '|' in raw_source:
            source_url = raw_source.split('|', 1)[1].strip()

        posted_date = None
        raw_date = data.get('posted_date')
        if raw_date:
            try:
                posted_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        try:
            JobOffer.objects.create(
                title=title,
                company=company,
                location=(data.get('location') or 'Maroc')[:255],
                sector=(data.get('sector') or '')[:255],
                description=data.get('description') or '',
                required_skills=data.get('required_skills') or '',
                required_education=data.get('required_education') or '',
                required_experience=(data.get('required_experience') or '')[:100],
                required_languages=data.get('required_languages') or '',
                contract_type=(data.get('contract_type') or '')[:100],
                posted_date=posted_date,
                source=source_site,
                source_url=source_url,
                is_active=True,
            )
            saved += 1
        except Exception as e:
            logger.warning(f"Offre non sauvegardée '{title}': {e}")

    return saved


def _build_results(offres_qs, profile_context: tuple) -> list:
    """Calcule les scores de matching et retourne la liste triée."""
    cv_text, cv_skills, cv_years, cv_ville = profile_context
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
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def _get_profile_context(user) -> tuple:
    """Retourne le contexte CV complet de l'utilisateur (même format que MatchingResultsView)."""
    try:
        from ..models import UserProfile as UP
        profile = UP.objects.prefetch_related('experiences').get(user=user)
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
        return cv_text, cv_skills, profile.experience_years or '', profile.ville or ''
    except Exception:
        return "", set(), "", ""


# ─────────────────────────────────────────────────────────────────
#  View principale
# ─────────────────────────────────────────────────────────────────

class JobSearchView(APIView):
    """
    Recherche d'offres d'emploi avec plusieurs modes :
      - source=dataset        : recherche dans les offres déjà en base
      - source=rekrute        : scraping temps réel rekrute.com (2 pages)
      - source=emploima       : scraping temps réel emploi.ma  (10 offres)
      - source=marocannonces  : scraping temps réel marocannonces.com (2 pages)
      - source=linkedin       : scraping temps réel LinkedIn (10 offres, Chrome)

    GET /api/jobs/search/?q=<keyword>&source=<dataset|rekrute|emploima|marocannonces|linkedin>
                           &location=<lieu>   (optionnel, utilisé par linkedin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keyword = request.query_params.get('q', '').strip()
        source = request.query_params.get('source', 'dataset').lower()

        if not keyword:
            return Response(
                {"error": "Le paramètre ?q= est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if source != 'dataset' and source not in VALID_SOURCES:
            return Response(
                {"error": f"Source invalide. Valeurs acceptées : dataset, {', '.join(VALID_SOURCES)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_context = _get_profile_context(request.user)

        # ── Mode dataset ─────────────────────────────────────────
        if source == 'dataset':
            offres_qs = (
                JobOffer.objects.filter(is_active=True, title__icontains=keyword)
                | JobOffer.objects.filter(is_active=True, sector__icontains=keyword)
                | JobOffer.objects.filter(is_active=True, location__icontains=keyword)
            ).distinct()

            results = _build_results(offres_qs, profile_context)

            # Sauvegarder dans l'historique
            best_score = results[0]['score'] if results else 0
            SearchHistory.objects.create(
                user=request.user,
                keyword=keyword,
                source=source,
                results_count=len(results),
                best_score=best_score,
            )

            return Response({
                "source": "dataset",
                "keyword": keyword,
                "count": len(results),
                "results": results,
            }, status=status.HTTP_200_OK)

        # ── Mode scraping temps réel ──────────────────────────────
        try:
            RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper, LinkedInScraper = _get_scrapers()
        except ImportError as e:
            return Response(
                {"error": "Dépendances de scraping non installées.", "detail": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        progress = _fresh_progress(keyword)
        raw_data = []

        try:
            if source == 'rekrute':
                scraper = RekruteScraper()
                raw_data = scraper.scrape(keyword, progress, pages=REALTIME_PAGES)

            elif source == 'marocannonces':
                scraper = MarocAnnoncesScraper()
                raw_data = scraper.scrape(keyword, progress, pages=REALTIME_PAGES)

            elif source == 'emploima':
                scraper = EmploiMaScraper()
                try:
                    raw_data = scraper.scrape(keyword, progress, max_offers=10)
                finally:
                    scraper.quit()

            elif source == 'linkedin':
                location_param = request.query_params.get('location', 'Morocco').strip() or 'Morocco'
                scraper = LinkedInScraper()
                try:
                    raw_data = scraper.scrape(
                        keyword, progress,
                        max_offers=10,
                        location=location_param,
                    )
                finally:
                    scraper.quit()

        except Exception as e:
            logger.error(f"Scraping [{source}] '{keyword}': {e}")
            return Response(
                {"error": "Erreur lors du scraping.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        new_count = _save_scraped_offers(raw_data, source_site=source)

        # Retourner toutes les offres de ce site correspondant au keyword
        offres_qs = (
            JobOffer.objects.filter(is_active=True, source=source, title__icontains=keyword)
            | JobOffer.objects.filter(is_active=True, source=source, sector__icontains=keyword)
        ).distinct()

        results = _build_results(offres_qs, profile_context)

        # Sauvegarder dans l'historique
        best_score = results[0]['score'] if results else 0
        SearchHistory.objects.create(
            user=request.user,
            keyword=keyword,
            source=source,
            results_count=len(results),
            best_score=best_score,
        )

        return Response({
            "source": source,
            "keyword": keyword,
            "new_offers_saved": new_count,
            "count": len(results),
            "results": results,
        }, status=status.HTTP_200_OK)

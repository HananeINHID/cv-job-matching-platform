"""
Views de recherche d'emplois.

Deux modes via le paramètre ?source= :
  - dataset                          → recherche dans les offres déjà en DB
  - rekrute | emploima | marocannonces → scraping temps réel (2 pages), sauvegarde en DB

Endpoint : GET /api/jobs/search/?q=<keyword>&source=<mode>
"""

import os
import sys
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile, JobOffer
from ..utils.matching_utils import parse_skills, cosine_score, tokenize_text

logger = logging.getLogger(__name__)

REALTIME_PAGES = 2
VALID_SOURCES = {'rekrute', 'emploima', 'marocannonces'}

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

    from scraping.emploi import RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper
    return RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper


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
                is_active=True,
            )
            saved += 1
        except Exception as e:
            logger.warning(f"Offre non sauvegardée '{title}': {e}")

    return saved


def _build_results(offres_qs, cv_tokens: list) -> list:
    """Calcule les scores de matching et retourne la liste triée."""
    results = []
    for offre in offres_qs:
        offer_skills = parse_skills(offre.required_skills)
        offer_desc_tokens = tokenize_text(offre.description or '')

        if cv_tokens:
            score_skills = cosine_score(cv_tokens, offer_skills + tokenize_text(offre.title))
            score_desc = cosine_score(cv_tokens, offer_desc_tokens)
            raw_score = score_skills * 0.70 + score_desc * 0.30
        else:
            raw_score = 0.5

        score_pct = round(min(raw_score * 100 * 1.5, 99))
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
            "source": offre.source,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def _get_cv_tokens(user) -> list:
    """Retourne les tokens CV de l'utilisateur (liste vide si profil absent)."""
    try:
        profile = UserProfile.objects.get(user=user)
        return parse_skills(profile.hard_skills) + tokenize_text(profile.titre or '')
    except UserProfile.DoesNotExist:
        return []


# ─────────────────────────────────────────────────────────────────
#  View principale
# ─────────────────────────────────────────────────────────────────

class JobSearchView(APIView):
    """
    Recherche d'offres d'emploi avec deux modes :
      - source=dataset     : recherche dans les offres déjà en base
      - source=rekrute     : scraping temps réel rekrute.com (2 pages)
      - source=emploima    : scraping temps réel emploi.ma  (10 offres)
      - source=marocannonces : scraping temps réel marocannonces.com (2 pages)

    GET /api/jobs/search/?q=<keyword>&source=<dataset|rekrute|emploima|marocannonces>
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

        cv_tokens = _get_cv_tokens(request.user)

        # ── Mode dataset ─────────────────────────────────────────
        if source == 'dataset':
            offres_qs = (
                JobOffer.objects.filter(is_active=True, title__icontains=keyword)
                | JobOffer.objects.filter(is_active=True, sector__icontains=keyword)
                | JobOffer.objects.filter(is_active=True, location__icontains=keyword)
            ).distinct()

            results = _build_results(offres_qs, cv_tokens)
            return Response({
                "source": "dataset",
                "keyword": keyword,
                "count": len(results),
                "results": results,
            }, status=status.HTTP_200_OK)

        # ── Mode scraping temps réel ──────────────────────────────
        try:
            RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper = _get_scrapers()
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

        results = _build_results(offres_qs, cv_tokens)
        return Response({
            "source": source,
            "keyword": keyword,
            "new_offers_saved": new_count,
            "count": len(results),
            "results": results,
        }, status=status.HTTP_200_OK)

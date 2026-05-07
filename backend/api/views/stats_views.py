"""
Views de statistiques et visualisation.

Endpoints :
  GET /api/stats/wordcloud/           → Top compétences demandées
  GET /api/stats/geo/                 → Distribution des offres par ville
  GET /api/stats/score-distribution/  → Histogramme des scores de matching
  GET /api/jobs/<id>/radar/           → Comparaison compétences CV vs offre
  GET /api/matching/clusters/         → Clustering K-means des offres
"""

import os
import logging
import pickle
from collections import Counter

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile, JobOffer
from ..utils.matching_utils import (
    parse_skills,
    compute_weighted_score,
    tokenize_text,
)

logger = logging.getLogger(__name__)

ML_MODELS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
    ),
    'ml_models'
)


def _load_pkl(filename):
    path = os.path.join(ML_MODELS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)


def _get_cv_context(user):
    """Retourne (cv_text, cv_skills_set, cv_years, cv_ville) pour l'utilisateur."""
    try:
        profile = UserProfile.objects.prefetch_related('experiences').get(user=user)
        exp_texts = " ".join([
            f"{e.poste or ''} {e.description or ''}"
            for e in profile.experiences.all()
        ])
        cv_text = " ".join(filter(None, [
            profile.titre or '', profile.hard_skills or '',
            profile.soft_skills or '', exp_texts,
        ]))
        cv_skills = set(parse_skills(profile.hard_skills))
        return cv_text, cv_skills, profile.experience_years or '', profile.ville or ''
    except UserProfile.DoesNotExist:
        return "", set(), "", ""


# ─────────────────────────────────────────────────────────────────

class WordCloudView(APIView):
    """
    Top compétences demandées dans toutes les offres actives.
    GET /api/stats/wordcloud/?limit=50
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        offres = JobOffer.objects.filter(is_active=True).values_list(
            'required_skills', flat=True
        )

        counter = Counter()
        for raw in offres:
            skills = parse_skills(raw or '')
            counter.update(skills)

        top_skills = [
            {"skill": skill.title(), "count": count}
            for skill, count in counter.most_common(limit)
        ]

        return Response({
            "count": len(top_skills),
            "skills": top_skills
        }, status=status.HTTP_200_OK)


class GeoDistributionView(APIView):
    """
    Distribution des offres actives par ville.
    GET /api/stats/geo/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        offres = JobOffer.objects.filter(is_active=True).values_list(
            'location', flat=True
        )

        counter = Counter(
            loc.strip().title() for loc in offres if loc and loc.strip()
        )

        cities = [
            {"ville": city, "count": count}
            for city, count in counter.most_common(30)
        ]

        return Response({
            "count": len(cities),
            "cities": cities
        }, status=status.HTTP_200_OK)


class ScoreDistributionView(APIView):
    """
    Distribution des scores de matching de l'utilisateur sur toutes les offres.
    GET /api/stats/score-distribution/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cv_text, cv_skills, cv_years, cv_ville = _get_cv_context(request.user)

        offres = JobOffer.objects.filter(is_active=True)
        buckets = {f"{i*10}-{i*10+10}": 0 for i in range(10)}

        for offre in offres:
            offer_text = " ".join(filter(None, [
                offre.title, offre.description, offre.required_skills
            ]))
            offer_skills = set(parse_skills(offre.required_skills))

            raw = compute_weighted_score(
                cv_text=cv_text, offer_text=offer_text,
                cv_skills=cv_skills, offer_skills=offer_skills,
                cv_years=cv_years, required_exp=offre.required_experience,
                cv_ville=cv_ville, offer_ville=offre.location,
            )
            score_pct = min(round(raw * 100 * 1.2), 99)
            bucket_idx = min(score_pct // 10, 9)
            key = f"{bucket_idx*10}-{bucket_idx*10+10}"
            buckets[key] += 1

        distribution = [
            {"range": k, "count": v} for k, v in buckets.items()
        ]

        return Response({
            "total_offers": offres.count(),
            "distribution": distribution
        }, status=status.HTTP_200_OK)


class RadarChartView(APIView):
    """
    Comparaison des compétences du profil CV vs une offre spécifique.
    GET /api/jobs/<id>/radar/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id):
        try:
            offre = JobOffer.objects.get(pk=offer_id, is_active=True)
        except JobOffer.DoesNotExist:
            return Response(
                {"error": "Offre introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        _, cv_skills, cv_years, cv_ville = _get_cv_context(request.user)

        offer_skills = set(parse_skills(offre.required_skills))
        matching = cv_skills & offer_skills
        cv_only = cv_skills - offer_skills
        offer_only = offer_skills - cv_skills

        # Score de l'offre
        try:
            profile = UserProfile.objects.get(user=request.user)
            cv_text = " ".join(filter(None, [
                profile.titre or '', profile.hard_skills or ''
            ]))
        except UserProfile.DoesNotExist:
            cv_text = ""

        offer_text = " ".join(filter(None, [
            offre.title, offre.description, offre.required_skills
        ]))
        raw = compute_weighted_score(
            cv_text=cv_text, offer_text=offer_text,
            cv_skills=cv_skills, offer_skills=offer_skills,
            cv_years=cv_years, required_exp=offre.required_experience,
            cv_ville=cv_ville, offer_ville=offre.location,
        )

        return Response({
            "offer": {
                "id": offre.id,
                "titre": offre.title,
                "entreprise": offre.company,
            },
            "cv_skills": sorted([s.title() for s in cv_skills]),
            "offer_skills": sorted([s.title() for s in offer_skills]),
            "matching_skills": sorted([s.title() for s in matching]),
            "cv_only": sorted([s.title() for s in cv_only]),
            "offer_only": sorted([s.title() for s in offer_only]),
            "match_rate": round(len(matching) / len(offer_skills) * 100) if offer_skills else 0,
            "score": min(round(raw * 100 * 1.2), 99),
        }, status=status.HTTP_200_OK)


class ClusterView(APIView):
    """
    Clustering K-means des offres en utilisant les modèles pré-entraînés
    stockés dans ml_models/ (kmeans_model.pkl + vectorizer_tfidf.pkl).
    GET /api/matching/clusters/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kmeans = _load_pkl('kmeans_model.pkl')
        vectorizer = _load_pkl('vectorizer_tfidf.pkl')

        if kmeans is None or vectorizer is None:
            return Response(
                {"error": "Modèles K-means non disponibles dans ml_models/."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        offres = list(JobOffer.objects.filter(is_active=True))
        if not offres:
            return Response({"clusters": []}, status=status.HTTP_200_OK)

        # Vectoriser les descriptions
        texts = [
            " ".join(filter(None, [o.title, o.required_skills, o.description]))
            for o in offres
        ]

        try:
            X = vectorizer.transform(texts)
            labels = kmeans.predict(X)
        except Exception as e:
            logger.error(f"K-means prediction error: {e}")
            return Response(
                {"error": "Erreur de prédiction K-means.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Regrouper les offres par cluster
        n_clusters = kmeans.n_clusters
        clusters = {i: {"id": i, "offers": [], "skills": Counter()} for i in range(n_clusters)}

        for offre, label in zip(offres, labels):
            label = int(label)
            skills = parse_skills(offre.required_skills)
            clusters[label]["skills"].update(skills)
            clusters[label]["offers"].append({
                "id": offre.id,
                "titre": offre.title,
                "entreprise": offre.company,
                "ville": offre.location,
            })

        result = []
        for c in clusters.values():
            top_skills = [s.title() for s, _ in c["skills"].most_common(5)]
            result.append({
                "id": c["id"],
                "size": len(c["offers"]),
                "top_skills": top_skills,
                "offers": c["offers"][:10],  # max 10 offres par cluster
            })

        result.sort(key=lambda x: x["size"], reverse=True)

        return Response({
            "n_clusters": n_clusters,
            "total_offers": len(offres),
            "clusters": result,
        }, status=status.HTTP_200_OK)

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

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

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


COMMON_SKILLS = {"react", "python", "javascript", "java", "sql", "node", "django", "docker", "aws", "angular", "vue", "php", "c++", "c#", "machine learning", "data", "devops", "kubernetes", "git", "linux", "agile", "scrum"}

def _get_offer_skills(offre):
    """Extrait les compétences de l'offre (utilise title/desc si required_skills est vide)."""
    skills = parse_skills(offre.required_skills)
    if not skills:
        text = f"{offre.title} {offre.description}".lower()
        skills = [s for s in COMMON_SKILLS if s in text]
    return skills


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
        for offre in JobOffer.objects.filter(is_active=True):
            skills = _get_offer_skills(offre)
            counter.update(skills)

        top_skills = [
            {"text": skill.title(), "value": count, "skill": skill.title(), "count": count}
            for skill, count in counter.most_common(limit)
        ]

        return Response(top_skills, status=status.HTTP_200_OK)


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
            offer_skills = set(_get_offer_skills(offre))

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

        labels = [k for k in buckets.keys()]
        counts = [v for v in buckets.values()]

        return Response({
            "labels": labels,
            "counts": counts
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

        offer_skills = set(_get_offer_skills(offre))
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

        # Création des axes pour le radar (max 6-7 compétences)
        # On priorise les compétences de l'offre
        all_axes = list(offer_skills)
        if len(all_axes) < 6:
            all_axes.extend(list(cv_skills - offer_skills))
        labels = [s.title() for s in all_axes[:7]]

        # Remplissage des données (100 si possède, 0 sinon)
        cv_data = [100 if s.lower() in [c.lower() for c in cv_skills] else 0 for s in labels]
        offre_data = [100 if s.lower() in [o.lower() for o in offer_skills] else 0 for s in labels]

        # Si l'offre n'a pas de compétences précises, on met un score par défaut
        if not labels:
            labels = ["Technique", "Expérience", "Outils", "Domaine", "Soft Skills"]
            cv_data = [70, 80, 60, 90, 85]
            offre_data = [80, 70, 70, 80, 90]

        return Response({
            "labels": labels,
            "cv": cv_data,
            "offre": offre_data,
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
            logger.warning(f"K-means predict failed, refitting: {e}")
            kmeans = KMeans(n_clusters=min(5, len(offres)), random_state=42)
            kmeans.fit(X)
            labels = kmeans.labels_
            
        try:
            # Réduction de dimension (PCA) pour affichage 2D
            pca = PCA(n_components=2, random_state=42)
            coords2d = pca.fit_transform(X.toarray())
        except Exception as e:
            logger.error(f"PCA error: {e}")
            return Response(
                {"error": "Erreur de PCA.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Identifier les top skills de chaque cluster pour le label
        n_clusters = kmeans.n_clusters
        cluster_skills = {i: Counter() for i in range(n_clusters)}
        for offre, label in zip(offres, labels):
            cluster_skills[int(label)].update(_get_offer_skills(offre))

        cluster_labels = {}
        for i in range(n_clusters):
            top = [s.title() for s, _ in cluster_skills[i].most_common(3)]
            cluster_labels[i] = " / ".join(top) if top else f"Cluster {i}"

        # Formater les données pour le frontend (Scatter plot)
        result = []
        for i, (offre, label, coords) in enumerate(zip(offres, labels, coords2d)):
            cluster_id = int(label)
            result.append({
                "x": round(float(coords[0]), 3),
                "y": round(float(coords[1]), 3),
                "cluster": cluster_id,
                "cluster_label": cluster_labels[cluster_id],
                "label": f"{offre.title} ({offre.company})"
            })

        # Le frontend attend un tableau (Array) directement
        return Response(result, status=status.HTTP_200_OK)

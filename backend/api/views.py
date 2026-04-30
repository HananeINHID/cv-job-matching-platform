import json
import math
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.db import transaction
from .models import UserProfile, JobOffer
from .serializers import UserProfileSerializer, UserRegistrationSerializer


class UserProfileView(APIView):
    """
    API View pour gérer le profil utilisateur (GET / POST / PUT).
    Endpoint: /api/profile/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Récupère le profil de l'utilisateur connecté."""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                "personal_info": {"nom": "", "email": "", "telephone": "", "ville": "", "titre": ""},
                "hard_skills": [],
                "soft_skills": [],
                "experiences": [],
                "formations": []
            }, status=status.HTTP_200_OK)
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Crée ou met à jour le profil de l'utilisateur connecté."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        except UserProfile.DoesNotExist:
            data = request.data.copy()
            data['user'] = request.user.id
            serializer = UserProfileSerializer(data=data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": "Erreur lors de la sauvegarde.", "detail": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Alias pour POST (mise à jour complète)."""
        return self.post(request)


class CVProfileView(APIView):
    """
    API View dédiée au formulaire CV (endpoint attendu par le frontend).
    Endpoint: /api/profile/cv/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Récupère le profil CV de l'utilisateur connecté."""
        try:
            profile = UserProfile.objects.prefetch_related('experiences', 'formations').get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                "personal_info": {"nom": "", "email": "", "telephone": "", "ville": "", "titre": ""},
                "hard_skills": [],
                "soft_skills": [],
                "experiences": [],
                "formations": []
            }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crée ou met à jour le profil CV avec toutes les données imbriquées.
        Payload attendu (même structure que le frontend):
        {
            "personal_info": {...},
            "hard_skills": [...],
            "soft_skills": [...],
            "experiences": [...],
            "formations": [...]
        }
        """
        try:
            profile = UserProfile.objects.prefetch_related('experiences', 'formations').get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data)
        except UserProfile.DoesNotExist:
            data = request.data.copy()
            data['user'] = request.user.id
            serializer = UserProfileSerializer(data=data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    profile = serializer.save(user=request.user)
                return Response({
                    "message": "Profil enregistré avec succès",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return Response(
                    {"error": "Erreur lors de la sauvegarde.", "detail": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Vue générique pour récupérer (GET) et mettre à jour (PUT/PATCH) 
    le profil de l'utilisateur authentifié.
    
    Endpoint: /api/profile/me/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retourne le profil de l'utilisateur connecté.
        Crée automatiquement un profil vide s'il n'existe pas.
        """
        profile, created = UserProfile.objects.prefetch_related(
            'experiences', 'formations'
        ).get_or_create(
            user=self.request.user,
            defaults={
                'nom': self.request.user.get_full_name() or self.request.user.username,
                'email': self.request.user.email
            }
        )
        return profile

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/profile/me/
        Récupère le profil complet avec expériences et formations.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH /api/profile/me/
        Met à jour le profil avec les données imbriquées.
        
        Payload attendu:
        {
            "personal_info": {"nom": "...", "email": "...", "telephone": "...", "ville": "...", "titre": "..."},
            "hard_skills": ["Python", "React"],
            "soft_skills": ["Communication"],
            "experiences": [{"poste": "...", "entreprise": "...", "debut": "...", "fin": "...", "description": "..."}],
            "formations": [{"diplome": "...", "etablissement": "...", "annee": "...", "domaine": "..."}]
        }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """PATCH - Mise à jour partielle."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class UserRegistrationView(APIView):
    """
    API View pour l'inscription d'un nouvel utilisateur avec vérification d'email.
    Endpoint: /api/auth/register/
    """
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def post(self, request):
        """
        Crée un nouvel utilisateur inactif et envoie l'email de vérification.
        
        Payload attendu:
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "motdepasse123",
            "password_confirm": "motdepasse123"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Inscription réussie. Veuillez vérifier votre email pour activer votre compte.",
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    API View pour vérifier l'email d'un utilisateur via token.
    Endpoint: /api/auth/verify-email/<uidb64>/<token>/
    """
    permission_classes = [AllowAny]  # CORRIGÉ : AllowAny requis pour endpoint public
    authentication_classes = []  # CORRIGÉ : désactiver authentification pour éviter 401 sur token invalide

    def get(self, request, uidb64, token):
        """
        Vérifie le token et active le compte utilisateur.
        
        Retourne 200 OK si succès, 400 Bad Request si token invalide.
        """
        try:
            # Décoder l'UID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                DjangoUnicodeDecodeError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({
                    "message": "Votre email est déjà vérifié. Vous pouvez vous connecter."
                }, status=status.HTTP_200_OK)
            
            # Activer le compte
            user.is_active = True
            user.save()
            
            # Créer automatiquement le profil utilisateur
            try:
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'nom': user.get_full_name() or user.username,
                        'email': user.email
                    }
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur création profil après vérification : {e}")
                # L'utilisateur est quand même activé, ne pas bloquer
            
            return Response({
                "message": "Email vérifié avec succès ! Votre compte est maintenant actif.",
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Le lien de vérification est invalide ou a expiré.",
            "detail": "Veuillez demander un nouvel email de vérification."
        }, status=status.HTTP_400_BAD_REQUEST)


# Utilitaires de matching

def _parse_skills(raw: str) -> list[str]:
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
    # Fallback CSV
    return [s.strip().lower() for s in raw.split(',') if s.strip()]


def _cosine_score(cv_tokens: list[str], offer_tokens: list[str]) -> float:
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


def _tokenize_text(text: str) -> list[str]:
    """Tokenize un texte libre en mots minuscules (sans ponctuation)."""
    import re
    return re.findall(r'\b[a-zA-ZÀ-ÿ0-9#+.]+\b', text.lower())



class MatchingResultsView(APIView):
    """
    Calcule et retourne les offres d'emploi triées par score de matching
    avec le profil CV de l'utilisateur connecté.

    Endpoint : GET /api/matching/results/?q=<mot_clé_optionnel>

    Algorithme :
      1. Charge le profil CV de l'utilisateur (hard_skills + titre)
      2. Pour chaque JobOffer active :
           - Extrait les required_skills + description
           - Calcule un score cosine skills (poids 70 %)
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

        #  1. Profil CV de l'utilisateur 
        try:
            profile = UserProfile.objects.get(user=request.user)
            cv_skills = _parse_skills(profile.hard_skills)
            cv_title_tokens = _tokenize_text(profile.titre or '')
            cv_tokens = cv_skills + cv_title_tokens
        except UserProfile.DoesNotExist:
            cv_tokens = []

        #  2. Offres actives 
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
            # Skills de l'offre
            offer_skills = _parse_skills(offre.required_skills)
            offer_desc_tokens = _tokenize_text(offre.description or '')

            if cv_tokens:
                score_skills = _cosine_score(cv_tokens, offer_skills + _tokenize_text(offre.title))
                score_desc = _cosine_score(cv_tokens, offer_desc_tokens)
                # Pondération : skills 70 % + description 30 %
                raw_score = score_skills * 0.70 + score_desc * 0.30
            else:
                # Profil vide : score neutre basé sur la popularité
                raw_score = 0.5

            score_pct = round(min(raw_score * 100 * 1.5, 99))  # normalise vers 0-99

            # Compétences requises à afficher (max 6)
            competences_display = [s.title() for s in offer_skills[:6]] if offer_skills else \
                _tokenize_text(offre.title)[:4]

            results.append({
                "id": offre.id,
                "titre": offre.title,
                "entreprise": offre.company,
                "ville": offre.location,
                "contrat": offre.contract_type or "CDI",
                "score": score_pct,
                "competences": competences_display,
            })

        #  4. Tri par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)

        return Response(results, status=status.HTTP_200_OK)

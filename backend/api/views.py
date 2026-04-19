from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.db import transaction
from .models import UserProfile
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
                    serializer.save()
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
                    profile = serializer.save()
                    if not hasattr(profile, 'user'):
                        profile.user = request.user
                        profile.save()
                return Response({
                    "message": "Profil enregistré avec succès",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
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

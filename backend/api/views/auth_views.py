"""
Views d'authentification.

Endpoints couverts :
  POST /api/auth/register/                          → UserRegistrationView
  GET  /api/auth/verify-email/<uidb64>/<token>/     → EmailVerificationView
"""

import logging

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile
from ..serializers import UserRegistrationSerializer

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    Inscription d'un nouvel utilisateur avec vérification d'email.
    Endpoint: POST /api/auth/register/
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Crée un nouvel utilisateur inactif et envoie l'email de vérification.

        Payload attendu:
        {
            "username": "hanane",
            "email": "hanane@gmail.com",
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
    Vérification de l'email d'un utilisateur via token.
    Endpoint: GET /api/auth/verify-email/<uidb64>/<token>/
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, uidb64, token):
        """
        Vérifie le token et active le compte utilisateur.

        Retourne 200 OK si succès, 400 Bad Request si token invalide.
        """
        try:
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

            user.is_active = True
            user.save()
            
            try:
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'nom': user.get_full_name() or user.username,
                        'email': user.email
                    }
                )
            except Exception as e:
                logger.error(f"Erreur création profil après vérification : {e}")

            return Response({
                "message": "Email vérifié avec succès ! Votre compte est maintenant actif.",
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Le lien de vérification est invalide ou a expiré.",
            "detail": "Veuillez demander un nouvel email de vérification."
        }, status=status.HTTP_400_BAD_REQUEST)

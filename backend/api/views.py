from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserProfileSerializer


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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            profile = serializer.save()
            if not hasattr(profile, 'user'):
                profile.user = request.user
                profile.save()
            return Response({
                "message": "Profil enregistré avec succès",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

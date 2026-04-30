from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import UserProfile, Experience, Education


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription d'un nouvel utilisateur avec vérification d'email.
    Crée un utilisateur inactif (is_active=False) jusqu'à confirmation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        """Vérifie que les mots de passe correspondent."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def validate_email(self, value):
        """Vérifie que l'email n'est pas déjà utilisé."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        """
        Crée un utilisateur et gère l'activation selon l'environnement :
        - DEBUG=True  (dev)  → is_active=True, pas d'email requis
        - DEBUG=False (prod) → is_active=False, vérification email obligatoire
        """
        # Vérification d'unicité du username
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError(
                {"username": "Ce nom d'utilisateur est déjà pris."}
            )

        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        is_dev = getattr(settings, 'DEBUG', False)

        # En dev : compte actif immédiatement
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            is_active=is_dev  # True en dev, False en prod
        )

        if not is_dev:
            # En production uniquement : envoi de l'email de vérification
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            self.send_verification_email(user.email, verification_link)

        return user

    def send_verification_email(self, email, verification_link):
        """Envoie l'email de vérification à l'utilisateur."""
        subject = 'Vérifiez votre compte CV Matching Platform'
        message = f"""
        Bonjour,

        Merci de vous être inscrit sur CV Matching Platform.
        Veuillez cliquer sur le lien ci-dessous pour vérifier votre email :

        {verification_link}

        Ce lien expire dans 24 heures.

        Si vous n'avez pas créé de compte, ignorez cet email.

        Cordialement,
        L'équipe CV Matching Platform
        """
        
        html_message = f"""
        <html>
        <body>
            <h2>Bienvenue sur CV Matching Platform !</h2>
            <p>Merci de vous être inscrit. Veuillez cliquer sur le bouton ci-dessous pour vérifier votre email :</p>
            <p><a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Vérifier mon email</a></p>
            <p>Ou copiez ce lien dans votre navigateur :<br>{verification_link}</p>
            <p><small>Ce lien expire dans 24 heures.</small></p>
        </body>
        </html>
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            import logging 
            logger = logging.getLogger(__name__) 
            logger.error(f"Erreur envoi email de vérification : {e}")


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer pour les expériences professionnelles."""
    
    class Meta:
        model = Experience
        fields = ['id', 'poste', 'entreprise', 'debut', 'fin', 'description']


class EducationSerializer(serializers.ModelSerializer):
    """Serializer pour les formations."""
    
    class Meta:
        model = Education
        fields = ['id', 'diplome', 'etablissement', 'annee', 'domaine']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour le profil utilisateur.
    Accepte et retourne la structure JSON 
    """
    personal_info = serializers.SerializerMethodField()
    hard_skills = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    soft_skills = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    experiences = ExperienceSerializer(many=True, required=False)
    formations = EducationSerializer(many=True, required=False)
    
    # Champs en lecture seule pour retourner les listes
    hard_skills_list = serializers.SerializerMethodField(read_only=True)
    soft_skills_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'personal_info',
            'hard_skills', 'hard_skills_list',
            'soft_skills', 'soft_skills_list',
            'experiences',
            'formations',
            'experience_years', 'sector', 'education_level',
            'job_title', 'languages', 'skills', 'certifications',
            'achievements', 'hobbies', 'interests', 'references', 'additional_info'
        ]

    def get_personal_info(self, obj):
        """Retourne les infos personnelles formatées comme attendu par le frontend."""
        return {
            'nom': obj.nom or '',
            'email': obj.email or '',
            'telephone': obj.telephone or '',
            'ville': obj.ville or '',
            'titre': obj.titre or ''
        }

    def get_hard_skills_list(self, obj):
        """Convertit le champ texte en liste JSON."""
        if not obj.hard_skills:
            return []
        try:
            import json
            return json.loads(obj.hard_skills)
        except (json.JSONDecodeError, TypeError):
            # Fallback: parser comme CSV si pas du JSON valide
            return [s.strip() for s in obj.hard_skills.split(',') if s.strip()]

    def get_soft_skills_list(self, obj):
        """Convertit le champ texte en liste JSON."""
        if not obj.soft_skills:
            return []
        try:
            import json
            return json.loads(obj.soft_skills)
        except (json.JSONDecodeError, TypeError):
            return [s.strip() for s in obj.soft_skills.split(',') if s.strip()]

    def create(self, validated_data):
        """
        Crée un profil complet avec toutes les relations imbriquées.
        """
        with transaction.atomic(): 
            # Extraire les données imbriquées
            experiences_data = validated_data.pop('experiences', [])
            formations_data = validated_data.pop('formations', [])
            hard_skills_list = validated_data.pop('hard_skills', [])
            soft_skills_list = validated_data.pop('soft_skills', [])

            # Gérer personal_info si fourni dans le payload
            personal_info = self.initial_data.get('personal_info', {})
            if personal_info:
                validated_data['nom'] = personal_info.get('nom', validated_data.get('nom'))
                validated_data['email'] = personal_info.get('email', validated_data.get('email'))
                validated_data['telephone'] = personal_info.get('telephone', validated_data.get('telephone'))
                validated_data['ville'] = personal_info.get('ville', validated_data.get('ville'))
                validated_data['titre'] = personal_info.get('titre', validated_data.get('titre'))

            # Sérialiser les skills en JSON
            import json
            if hard_skills_list:
                validated_data['hard_skills'] = json.dumps(hard_skills_list)
            if soft_skills_list:
                validated_data['soft_skills'] = json.dumps(soft_skills_list)

            # Créer le profil
            profile = UserProfile.objects.create(**validated_data)

            # Créer les expériences associées
            for exp_data in experiences_data:
                Experience.objects.create(profile=profile, **exp_data)

            # Créer les formations associées
            for form_data in formations_data:
                Education.objects.create(profile=profile, **form_data)

            return profile

    def update(self, instance, validated_data):
        """
        Met à jour un profil complet avec toutes les relations imbriquées.
        Gère: personal_info, hard_skills, soft_skills, experiences, formations
        """
        with transaction.atomic():
            # Extraire les données imbriquées
            experiences_data = validated_data.pop('experiences', None)
            formations_data = validated_data.pop('formations', None)
            hard_skills_list = validated_data.pop('hard_skills', None)
            soft_skills_list = validated_data.pop('soft_skills', None)

            # Gérer personal_info
            personal_info = self.initial_data.get('personal_info', {})
            if personal_info:
                instance.nom = personal_info.get('nom', instance.nom)
                instance.email = personal_info.get('email', instance.email)
                instance.telephone = personal_info.get('telephone', instance.telephone)
                instance.ville = personal_info.get('ville', instance.ville)
                instance.titre = personal_info.get('titre', instance.titre)

            # Mettre à jour les champs simples
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # Mettre à jour les skills (sérialisés en JSON)
            import json
            if hard_skills_list is not None:
                instance.hard_skills = json.dumps(hard_skills_list) if hard_skills_list else ''
            if soft_skills_list is not None:
                instance.soft_skills = json.dumps(soft_skills_list) if soft_skills_list else ''

            instance.save()

            # Mettre à jour les expériences (suppression et recréation pour simplifier)
            if experiences_data is not None:
                instance.experiences.all().delete()
                for exp_data in experiences_data:
                    Experience.objects.create(profile=instance, **exp_data)

            # Mettre à jour les formations (suppression et recréation pour simplifier)
            if formations_data is not None:
                instance.formations.all().delete()
                for form_data in formations_data:
                    Education.objects.create(profile=instance, **form_data)

            return instance

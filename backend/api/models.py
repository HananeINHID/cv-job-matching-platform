from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Profil utilisateur avec informations personnelles et compétences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Informations personnelles
    nom = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    ville = models.CharField(max_length=255, blank=True, null=True)
    titre = models.CharField(max_length=255, blank=True, null=True, 
                              help_text="Titre du poste recherché")
    
    # Compétences stockées en JSON ou texte séparé par virgules
    hard_skills = models.TextField(blank=True, null=True, 
                                   help_text="Compétences techniques (format JSON ou CSV)")
    soft_skills = models.TextField(blank=True, null=True,
                                   help_text="Compétences humaines (format JSON ou CSV)")

    experience_years = models.CharField(max_length=100, blank=True) 
    sector = models.CharField(max_length=255, blank=True)          
    education_level = models.CharField(max_length=100, blank=True) 
    job_title = models.CharField(max_length=255, blank=True)        
    languages = models.TextField(blank=True)                        
    skills = models.TextField(blank=True)                       
    certifications = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    hobbies = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    references = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return f"Profil de {self.nom or self.user.username}"


class Experience(models.Model):
    """Expérience professionnelle liée à un profil utilisateur."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, 
                                related_name='experiences')
    poste = models.CharField(max_length=255, blank=True, null=True)
    entreprise = models.CharField(max_length=255, blank=True, null=True)
    debut = models.CharField(max_length=20, blank=True, null=True,
                             help_text="Format: YYYY-MM")
    fin = models.CharField(max_length=20, blank=True, null=True,
                           help_text="Format: YYYY-MM (vide si en cours)")
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-debut']

    def __str__(self):
        return f"{self.poste} - {self.entreprise}"


class Education(models.Model):
    """Formation/Éducation liée à un profil utilisateur."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, 
                                related_name='formations')
    diplome = models.CharField(max_length=255, blank=True, null=True)
    etablissement = models.CharField(max_length=255, blank=True, null=True)
    annee = models.CharField(max_length=10, blank=True, null=True,
                             help_text="Année d'obtention")
    domaine = models.CharField(max_length=255, blank=True, null=True,
                               help_text="Domaine d'étude")
    
    class Meta:
        ordering = ['-annee']

    def __str__(self):
        return f"{self.diplome} - {self.etablissement}"


class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    sector = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    
    required_skills = models.TextField(blank=True)
    required_education = models.TextField(blank=True)    
    required_experience = models.CharField(max_length=100, blank=True)
    required_languages = models.TextField(blank=True)    
    
    contract_type = models.CharField(max_length=100, blank=True)
    posted_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.company}"
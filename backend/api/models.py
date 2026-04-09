from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
        return f"Profil de {self.user.username}"
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
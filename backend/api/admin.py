from django.contrib import admin
from .models import UserProfile, Experience, Education


class ExperienceInline(admin.TabularInline):
    """Affichage inline des expériences dans la page profil."""
    model = Experience
    extra = 0
    fields = ['poste', 'entreprise', 'debut', 'fin']
    ordering = ['-debut']


class EducationInline(admin.TabularInline):
    """Affichage inline des formations dans la page profil."""
    model = Education
    extra = 0
    fields = ['diplome', 'etablissement', 'annee', 'domaine']
    ordering = ['-annee']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin pour les profils utilisateurs avec affichage des relations."""
    list_display = ['user', 'nom', 'email', 'ville', 'titre', 'get_experience_count', 'get_formation_count']
    list_filter = ['ville', 'sector']
    search_fields = ['nom', 'email', 'user__username', 'titre']
    inlines = [ExperienceInline, EducationInline]
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'email', 'telephone', 'ville', 'titre')
        }),
        ('Compétences', {
            'fields': ('hard_skills', 'soft_skills')
        }),
        ('Champs legacy', {
            'classes': ('collapse',),
            'fields': ('experience_years', 'sector', 'education_level', 'job_title', 
                       'languages', 'skills', 'certifications', 'achievements',
                       'hobbies', 'interests', 'references', 'additional_info')
        }),
    )
    
    def get_experience_count(self, obj):
        """Retourne le nombre d'expériences du profil."""
        return obj.experiences.count()
    get_experience_count.short_description = 'Expériences'
    
    def get_formation_count(self, obj):
        """Retourne le nombre de formations du profil."""
        return obj.formations.count()
    get_formation_count.short_description = 'Formations'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin standalone pour les expériences (optionnel)."""
    list_display = ['poste', 'entreprise', 'debut', 'fin', 'profile']
    list_filter = ['debut', 'fin']
    search_fields = ['poste', 'entreprise', 'profile__nom']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin standalone pour les formations (optionnel)."""
    list_display = ['diplome', 'etablissement', 'annee', 'domaine', 'profile']
    list_filter = ['annee', 'domaine']
    search_fields = ['diplome', 'etablissement', 'profile__nom']

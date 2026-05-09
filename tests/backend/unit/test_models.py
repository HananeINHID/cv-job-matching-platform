"""
test_models.py — Tests unitaires des modèles Django.

Périmètre :
  - UserProfile      : création, champs JSON skills, __str__
  - Experience       : relation FK, cascade delete
  - Education        : relation FK, cascade delete
  - JobOffer         : création, champs optionnels
  - SearchHistory    : création, ordering

Utilise la DB de test (SQLite en mémoire via pytest-django).
"""

import json
import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from api.models import UserProfile, Experience, Education, JobOffer, SearchHistory


pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════
#  USERPROFILE
# ═══════════════════════════════════════════════════════════

class TestUserProfileModel:

    def test_create_user_profile_all_fields(self):
        """Création d'un UserProfile avec tous les champs → sauvegarde OK."""
        user = User.objects.create_user("alice", "alice@test.com", "pass1234")
        profile = UserProfile.objects.create(
            user=user,
            nom="Alice Martin",
            email="alice@test.com",
            telephone="+212 600000001",
            ville="Rabat",
            titre="Data Engineer",
            hard_skills=json.dumps(["python", "sql", "spark"]),
            soft_skills=json.dumps(["leadership", "communication"]),
            experience_years="4 ans",
            sector="IT",
            education_level="Master",
        )
        assert profile.pk is not None
        assert profile.nom == "Alice Martin"
        assert profile.ville == "Rabat"

    def test_user_profile_str_returns_nom(self):
        """__str__ retourne 'Profil de <nom>'."""
        user = User.objects.create_user("bob", "bob@test.com", "pass1234")
        profile = UserProfile.objects.create(user=user, nom="Bob Dupont")
        assert "Bob Dupont" in str(profile)

    def test_user_profile_str_fallback_to_username(self):
        """__str__ utilise le username si nom est vide."""
        user = User.objects.create_user("charlie", "charlie@test.com", "pass1234")
        profile = UserProfile.objects.create(user=user)
        assert "charlie" in str(profile)

    def test_hard_skills_stored_as_json_string(self):
        """hard_skills stocké en JSON → récupéré comme chaîne JSON, parsable en liste."""
        user = User.objects.create_user("diana", "diana@test.com", "pass1234")
        skills_list = ["react", "javascript", "typescript"]
        profile = UserProfile.objects.create(
            user=user,
            hard_skills=json.dumps(skills_list),
        )
        # Récupération depuis DB
        saved = UserProfile.objects.get(pk=profile.pk)
        parsed = json.loads(saved.hard_skills)
        assert parsed == skills_list

    def test_soft_skills_stored_as_json_string(self):
        """soft_skills stocké en JSON → récupéré et parsable."""
        user = User.objects.create_user("eve", "eve@test.com", "pass1234")
        skills = ["empathie", "communication"]
        profile = UserProfile.objects.create(user=user, soft_skills=json.dumps(skills))
        saved = UserProfile.objects.get(pk=profile.pk)
        assert json.loads(saved.soft_skills) == skills

    def test_user_profile_one_to_one_with_user(self):
        """UserProfile est OneToOne avec User."""
        user = User.objects.create_user("frank", "frank@test.com", "pass1234")
        UserProfile.objects.create(user=user, nom="Frank")
        # Impossible de créer un 2ème profil pour le même user
        with pytest.raises(Exception):
            UserProfile.objects.create(user=user, nom="Frank Duplicate")

    def test_user_profile_deleted_on_user_delete(self):
        """Suppression User → cascade delete sur UserProfile."""
        user = User.objects.create_user("grace", "grace@test.com", "pass1234")
        profile = UserProfile.objects.create(user=user, nom="Grace")
        pk = profile.pk
        user.delete()
        assert not UserProfile.objects.filter(pk=pk).exists()

    def test_blank_optional_fields_allowed(self):
        """Les champs optionnels peuvent être vides."""
        user = User.objects.create_user("henry", "henry@test.com", "pass1234")
        profile = UserProfile.objects.create(user=user)
        assert profile.pk is not None
        assert profile.nom is None or profile.nom == ""


# ═══════════════════════════════════════════════════════════
#  EXPERIENCE
# ═══════════════════════════════════════════════════════════

class TestExperienceModel:

    def setup_method(self):
        self.user = User.objects.create_user("exp_user", "exp@test.com", "pass1234")
        self.profile = UserProfile.objects.create(user=self.user, nom="Exp User")

    def test_create_experience_linked_to_profile(self):
        """Création d'une Experience liée à un UserProfile → FK correcte."""
        exp = Experience.objects.create(
            profile=self.profile,
            poste="Développeur Backend",
            entreprise="TechCo",
            debut="2022-01",
            fin="2024-01",
            description="Développement d'APIs REST avec Django",
        )
        assert exp.pk is not None
        assert exp.profile == self.profile

    def test_experience_str_representation(self):
        """__str__ retourne 'poste - entreprise'."""
        exp = Experience.objects.create(
            profile=self.profile,
            poste="Data Analyst",
            entreprise="AnalytiCo",
        )
        assert "Data Analyst" in str(exp)
        assert "AnalytiCo" in str(exp)

    def test_experience_cascade_delete_on_profile_delete(self):
        """Suppression UserProfile → cascade delete sur Experience."""
        exp = Experience.objects.create(
            profile=self.profile,
            poste="Engineer",
            entreprise="Corp",
        )
        exp_pk = exp.pk
        self.profile.delete()
        assert not Experience.objects.filter(pk=exp_pk).exists()

    def test_multiple_experiences_per_profile(self):
        """Un profil peut avoir plusieurs expériences."""
        Experience.objects.create(profile=self.profile, poste="Junior Dev", entreprise="A")
        Experience.objects.create(profile=self.profile, poste="Senior Dev", entreprise="B")
        count = Experience.objects.filter(profile=self.profile).count()
        assert count == 2

    def test_experience_optional_fields_blank(self):
        """Les champs optionnels peuvent être vides."""
        exp = Experience.objects.create(profile=self.profile)
        assert exp.pk is not None


# ═══════════════════════════════════════════════════════════
#  EDUCATION
# ═══════════════════════════════════════════════════════════

class TestEducationModel:

    def setup_method(self):
        self.user = User.objects.create_user("edu_user", "edu@test.com", "pass1234")
        self.profile = UserProfile.objects.create(user=self.user, nom="Edu User")

    def test_create_education_linked_to_profile(self):
        """Création d'une Education liée à un UserProfile → FK correcte."""
        edu = Education.objects.create(
            profile=self.profile,
            diplome="Master IASD",
            etablissement="FSS Marrakech",
            annee="2024",
            domaine="Intelligence Artificielle",
        )
        assert edu.pk is not None
        assert edu.profile == self.profile

    def test_education_str_representation(self):
        """__str__ retourne 'diplome - etablissement'."""
        edu = Education.objects.create(
            profile=self.profile,
            diplome="Licence Informatique",
            etablissement="UCA",
        )
        assert "Licence Informatique" in str(edu)
        assert "UCA" in str(edu)

    def test_education_cascade_delete_on_profile_delete(self):
        """Suppression UserProfile → cascade delete sur Education."""
        edu = Education.objects.create(
            profile=self.profile,
            diplome="BTS",
            etablissement="Institut Tech",
        )
        edu_pk = edu.pk
        self.profile.delete()
        assert not Education.objects.filter(pk=edu_pk).exists()

    def test_multiple_formations_per_profile(self):
        """Un profil peut avoir plusieurs formations."""
        Education.objects.create(profile=self.profile, diplome="Bac", etablissement="Lycée")
        Education.objects.create(profile=self.profile, diplome="Licence", etablissement="Fac")
        assert Education.objects.filter(profile=self.profile).count() == 2


# ═══════════════════════════════════════════════════════════
#  JOBOFFER
# ═══════════════════════════════════════════════════════════

class TestJobOfferModel:

    def test_create_job_offer_minimal(self):
        """Création d'une JobOffer avec les champs obligatoires → sauvegarde OK."""
        offer = JobOffer.objects.create(
            title="Data Scientist",
            company="CAT Assurance",
            location="Casablanca",
            description="Analyse de données avec Python.",
        )
        assert offer.pk is not None

    def test_job_offer_default_is_active(self):
        """is_active est True par défaut."""
        offer = JobOffer.objects.create(
            title="Dev", company="Corp", location="Rabat", description="..."
        )
        assert offer.is_active is True

    def test_job_offer_str_representation(self):
        """__str__ retourne 'title - company'."""
        offer = JobOffer.objects.create(
            title="ML Engineer", company="StartupAI", location="Agadir", description="..."
        )
        assert "ML Engineer" in str(offer)
        assert "StartupAI" in str(offer)

    def test_job_offer_optional_fields_default_empty(self):
        """Les champs optionnels ont une valeur par défaut vide."""
        offer = JobOffer.objects.create(
            title="Dev", company="Corp", location="Rabat", description="..."
        )
        assert offer.required_skills == "" or offer.required_skills is None or offer.required_skills == ""
        assert offer.contract_type == "" or offer.contract_type is None

    def test_job_offer_source_url_optional(self):
        """source_url peut être vide."""
        offer = JobOffer.objects.create(
            title="Chef de Projet",
            company="AgenceWeb",
            location="Fès",
            description="Gestion de projets digitaux.",
            source_url="",
        )
        assert offer.pk is not None

    def test_job_offer_filter_active(self):
        """Filtre is_active=True retourne uniquement les offres actives."""
        JobOffer.objects.create(title="A", company="X", location="Y", description=".", is_active=True)
        JobOffer.objects.create(title="B", company="X", location="Y", description=".", is_active=False)
        active = JobOffer.objects.filter(is_active=True)
        inactive = JobOffer.objects.filter(is_active=False)
        assert active.count() >= 1
        assert inactive.count() >= 1


# ═══════════════════════════════════════════════════════════
#  SEARCHHISTORY
# ═══════════════════════════════════════════════════════════

class TestSearchHistoryModel:

    def test_create_search_history(self):
        """Création d'un SearchHistory → sauvegarde OK."""
        user = User.objects.create_user("hist_user", "hist@test.com", "pass1234")
        entry = SearchHistory.objects.create(
            user=user,
            keyword="Data Scientist",
            source="rekrute",
            results_count=12,
        )
        assert entry.pk is not None
        assert entry.keyword == "Data Scientist"
        assert entry.results_count == 12

    def test_search_history_ordered_by_searched_at_desc(self):
        """Les entrées sont triées par searched_at décroissant."""
        user = User.objects.create_user("ord_user", "ord@test.com", "pass1234")
        SearchHistory.objects.create(user=user, keyword="Python", source="dataset", results_count=5)
        SearchHistory.objects.create(user=user, keyword="Django", source="rekrute", results_count=3)
        SearchHistory.objects.create(user=user, keyword="ML", source="emploima", results_count=8)

        entries = list(SearchHistory.objects.filter(user=user))
        # Le dernier créé doit être en premier (ordering=-searched_at)
        assert entries[0].keyword == "ML"

    def test_search_history_str_contains_keyword(self):
        """__str__ contient le keyword."""
        user = User.objects.create_user("str_user", "str@test.com", "pass1234")
        entry = SearchHistory.objects.create(
            user=user, keyword="React Developer", source="dataset", results_count=7
        )
        assert "React Developer" in str(entry)

    def test_search_history_cascade_delete_on_user_delete(self):
        """Suppression User → cascade delete sur SearchHistory."""
        user = User.objects.create_user("del_user", "del@test.com", "pass1234")
        entry = SearchHistory.objects.create(
            user=user, keyword="test", source="dataset", results_count=0
        )
        pk = entry.pk
        user.delete()
        assert not SearchHistory.objects.filter(pk=pk).exists()

    def test_search_history_default_source_is_dataset(self):
        """Source par défaut = 'dataset'."""
        user = User.objects.create_user("def_user", "def@test.com", "pass1234")
        entry = SearchHistory.objects.create(user=user, keyword="test", results_count=0)
        assert entry.source == "dataset"

from django.urls import path
from .views import UserProfileView, CVProfileView, UserProfileRetrieveUpdateView


urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/cv/', CVProfileView.as_view(), name='cv-profile'),
    path('profile/me/', UserProfileRetrieveUpdateView.as_view(), name='user-profile-me'),
]

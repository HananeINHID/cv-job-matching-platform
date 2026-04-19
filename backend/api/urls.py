from django.urls import path
from .views import (
    UserProfileView, 
    CVProfileView, 
    UserProfileRetrieveUpdateView,
    UserRegistrationView,
    EmailVerificationView
)


urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/cv/', CVProfileView.as_view(), name='cv-profile'),
    path('profile/me/', UserProfileRetrieveUpdateView.as_view(), name='user-profile-me'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/verify-email/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
]

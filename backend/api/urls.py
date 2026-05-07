from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserProfileView,
    CVProfileView,
    UserProfileRetrieveUpdateView,
    UserRegistrationView,
    EmailVerificationView,
    MatchingResultsView,
    JobSearchView,
    WordCloudView,
    GeoDistributionView,
    ScoreDistributionView,
    RadarChartView,
    ClusterView,
)


urlpatterns = [
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/verify-email/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),

    # Profil utilisateur
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/cv/', CVProfileView.as_view(), name='cv-profile'),
    path('profile/me/', UserProfileRetrieveUpdateView.as_view(), name='user-profile-me'),

    # Matching & recherche
    path('matching/results/', MatchingResultsView.as_view(), name='matching-results'),
    path('matching/clusters/', ClusterView.as_view(), name='matching-clusters'),
    path('jobs/search/', JobSearchView.as_view(), name='job-search'),
    path('jobs/<int:offer_id>/radar/', RadarChartView.as_view(), name='job-radar'),

    # Statistiques & visualisation
    path('stats/wordcloud/', WordCloudView.as_view(), name='stats-wordcloud'),
    path('stats/geo/', GeoDistributionView.as_view(), name='stats-geo'),
    path('stats/score-distribution/', ScoreDistributionView.as_view(), name='stats-score-distribution'),
]

"""
Package views — réexporte toutes les classes pour compatibilité avec urls.py.

Permet d'importer directement depuis `api.views` sans changer urls.py :
    from .views import UserProfileView, CVProfileView, ...
"""

from .auth_views import (
    UserRegistrationView,
    EmailVerificationView,
)
from .profile_views import (
    UserProfileView,
    CVProfileView,
    UserProfileRetrieveUpdateView,
)
from .matching_views import (
    MatchingResultsView,
)
from .job_search_views import (
    JobSearchView,
)
from .stats_views import (
    WordCloudView,
    GeoDistributionView,
    ScoreDistributionView,
    RadarChartView,
    ClusterView,
)

__all__ = [
    "UserRegistrationView",
    "EmailVerificationView",
    "UserProfileView",
    "CVProfileView",
    "UserProfileRetrieveUpdateView",
    "MatchingResultsView",
    "JobSearchView",
    "WordCloudView",
    "GeoDistributionView",
    "ScoreDistributionView",
    "RadarChartView",
    "ClusterView",
]

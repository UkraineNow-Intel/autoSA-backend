from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views


class OptionalSlashRouter(DefaultRouter):
    """Make all trailing slashes optional in the URLs used by the viewsets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register("sources", views.SourceViewSet)
router.register("translations", views.TranslationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

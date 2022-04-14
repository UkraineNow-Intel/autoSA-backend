from rest_framework import viewsets
from .serializers import SourceSerializer, TranslationSerializer, LocationSerializer
from .models import Source, Translation, Location
import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from django_filters import CharFilter
from django.db.models import Q
from django_filters.rest_framework import FilterSet


def getPermissionsForUser(user):
    """
    Returns a list of all permissions for a user, e.g.:
    `[{id: 1, name 'Can log entry', content_type_id: 1, codename: 'add_logentry'}, ...]`
    """
    if user.is_superuser:
        return list(Permission.objects.all().values())
    permissions = user.user_permissions.all() | Permission.objects.filter(
        group__user=user
    )
    return list(permissions.values())


class WhoAmIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, format=None):
        current_permissions = getPermissionsForUser(request.user)
        return JsonResponse(
            {
                "username": request.user.username,
                "isAuthenticated": True,
                "permissions": current_permissions,
            }
        )


@ensure_csrf_cookie
def get_csrf(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["X-CSRFToken"] = get_token(request)
    return response


@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    if username is None or password is None:
        return JsonResponse(
            {"detail": "Please provide username and password."}, status=400
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=400)

    login(request, user)
    current_permissions = getPermissionsForUser(request.user)
    return JsonResponse(
        {
            "detail": "Successfully logged in.",
            "username": request.user.username,
            "permissions": current_permissions,
        }
    )


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "You're not logged in."}, status=400)

    logout(request)
    return JsonResponse({"detail": "Successfully logged out."})


class TagsFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            tags = [tag.strip().lower() for tag in value.split(",")]
            qs = qs.filter(tags__name__in=tags).distinct()

        return qs


class SourceFilter(FilterSet):
    """Filter for Sources"""

    tags = TagsFilter("tags")
    q = CharFilter(method="multi_field_search", lookup_expr="icontains")

    def multi_field_search(self, queryset, name, value):
        """Search in headline, text or tags"""
        return queryset.filter(
            Q(text__icontains=value) |
            Q(headline__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()

    class Meta:
        model = Source
        fields = {
            "interface": ["exact"],
            "source": ["exact"],
            "headline": ["exact", "contains", "icontains"],
            "text": ["exact", "contains", "icontains"],
            "timestamp": ["exact", "lt", "lte", "gt", "gte", "range"],
        }


class SourceViewSet(viewsets.ModelViewSet):
    """List or retrieve sources"""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [DjangoModelPermissions]
    filterset_class = SourceFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by("-timestamp")


class TranslationViewSet(viewsets.ModelViewSet):
    """List or retrieve translations"""

    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

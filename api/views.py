from rest_framework import viewsets
from .serializers import SourceSerializer, TranslationSerializer
from .models import Source, Translation
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
from django.conf import settings
from django.db.models import Q
from django_filters.rest_framework import FilterSet
from infotools.webscraping import webscraper
from psqlextra.query import ConflictAction


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


def refresh(request):
    """Gets new data from different interfaces and adds it to the database.
    If "overwrite==true" and items have the same external_id, they will be
    updated.
    """
    overwrite_existing = request.GET.get("overwrite", "false") in ("true", "1")
    conflict_action = (
        ConflictAction.UPDATE if overwrite_existing else ConflictAction.NOTHING
    )

    response_data = {}
    failed_items = []
    for site_key in settings.WEBSCRAPER_SITE_KEYS:
        data = webscraper.get_latest(site_key)
        processed = 0
        for item in data:
            try:
                Source.objects.on_conflict(
                    ["external_id"], conflict_action
                ).insert_and_get(**item)
                processed += 1
            except Exception as x:
                # log exception, do not raise
                failed_items.append(
                    {
                        "item": item,
                        "exception_class": x.__class__.__name__,
                        "exception_message": str(x),
                    }
                )
        response_data[site_key] = {
            "detail": "Refresh completed",
            "overwrite": overwrite_existing,
            "processed": processed,
            "errors": {
                "total": len(failed_items),
                "items": failed_items,
            },
        }
    return JsonResponse(response_data)


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

    @property
    def qs(self):
        parent = super().qs
        deleted_val = self.request.GET.get("deleted", "false").lower()
        if deleted_val == "any":
            return parent
        deleted_bool = {"true": True, "false": False, "1": True, "0": False}.get(
            deleted_val, False
        )
        return parent.filter(deleted=deleted_bool)

    def multi_field_search(self, queryset, name, value):
        """Search in headline, text or tags"""
        return queryset.filter(
            Q(text__icontains=value)
            | Q(headline__icontains=value)
            | Q(tags__name__icontains=value)
        ).distinct()

    class Meta:
        model = Source
        fields = {
            "interface": ["exact"],
            "origin": ["exact"],
            "headline": ["exact", "contains", "icontains"],
            "text": ["exact", "contains", "icontains"],
            "timestamp": ["exact", "lt", "lte", "gt", "gte", "range"],
            "deleted": ["exact"],
            "pinned": ["exact"],
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

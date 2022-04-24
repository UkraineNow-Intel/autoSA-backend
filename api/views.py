import datetime as dt
import json
import logging

import dateparser
import pytz
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from more_itertools import chunked
from psqlextra.query import ConflictAction
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.views import APIView
from taggit.models import Tag

from infotools.telegram import telegram
from infotools.twitter import twitter
from infotools.webscraping import webscraper

from .models import Source, Translation
from .serializers import SourceSerializer, TagSerializer, TranslationSerializer

INSERT_BATCH_SIZE = 500
logger = logging.getLogger(__name__)


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


def _default_refresh_start_time():
    """By default, retrieve from 24 hours back until now."""
    return (dt.datetime.utcnow() - dt.timedelta(hours=24)).replace(tzinfo=pytz.UTC)


def _oldest_refresh_start_time():
    """We can look from 7 days back until now."""
    return (dt.datetime.utcnow() - dt.timedelta(days=7)).replace(tzinfo=pytz.UTC)


def _parse_refresh_time(date_string, default_value=None, oldest_value=None):
    """Parse provided datetime from string. If can't parse, fallback to default."""
    try:
        if date_string:
            res = dateparser.parse(date_string)
            if oldest_value and res < oldest_value:
                # twitter search will error out if we search earlier than
                # oldest_value. Don't set value at all in this case.
                res = None
        else:
            res = default_value
        return res
    except Exception:
        logger.exception("Unable to parse date: %s", date_string)
        return default_value


# TODO: refactor, this is now too long, move the logic to a class
def refresh(request):
    """Gets new data from different interfaces and adds it to the database.
    If "overwrite==true" and items have the same external_id, they will be
    updated.
    Other parameters:
        start_time (example: 2022-04-11 or 2022-04-11T00:00:00Z)
        end_time (example: 2022-04-12 or 2022-04-12T00:00:00Z)
    """
    overwrite_existing = request.GET.get("overwrite", "false") in ("true", "1")
    start_time = request.GET.get("start_time", None)
    end_time = request.GET.get("end_time", None)

    start_time = _parse_refresh_time(
        start_time, _default_refresh_start_time(), _oldest_refresh_start_time()
    )
    end_time = _parse_refresh_time(end_time, None)

    logger.info(
        "Refresh started with start_time: %s, end_time: %s, overwrite: %s",
        start_time,
        end_time,
        overwrite_existing,
    )

    conflict_action = (
        ConflictAction.UPDATE if overwrite_existing else ConflictAction.NOTHING
    )

    response_data = {
        "sites": {},
        "meta": {
            "overwrite": overwrite_existing,
            "start_time": start_time,
            "end_time": end_time,
        },
    }

    def add_response_error(x: Exception, errors: list):
        """Append error to list for site"""
        errors.append(
            {
                "exception_class": x.__class__.__name__,
                "exception_message": str(x),
            }
        )

    def add_response_data(key, processed, errors):
        """Append data to response for site"""
        response_data["sites"][key] = {
            "detail": "Refresh completed",
            "processed": processed,
            "errors": {
                "total": len(errors),
                "exceptions": errors,
            },
        }

    def insert_chunk(chunk, errors):
        """Insert chunk of data. If fails, append exception to errors."""
        logger.info("Inserting %s records", len(chunk))
        try:
            (
                Source.objects.on_conflict(
                    ["external_id"], conflict_action
                ).bulk_insert(chunk)
            )
        except Exception as x:
            # log exception, do not raise
            add_response_error(x, errors)
            logger.exception("Failed inserting data.")
            for value in chunk:
                logger.debug(str(value))
        return errors

    # web scraper data
    for site_key in settings.WEBSCRAPER_SITE_KEYS:
        processed = 0
        errors = []
        data = webscraper.get_latest(site_key)
        for chunk in chunked(data, INSERT_BATCH_SIZE):
            errors = insert_chunk(chunk, errors)
            processed += len(chunk)
        add_response_data(site_key, processed, errors)

    # twitter data
    twitter_settings = {
        "TWITTER_BEARER_TOKEN": settings.TWITTER_BEARER_TOKEN,
    }
    processed = 0
    errors = []
    try:
        tweets = twitter.search_recent_tweets(
            twitter_settings, start_time=start_time, end_time=end_time
        )
        for chunk in chunked(tweets, INSERT_BATCH_SIZE):
            errors = insert_chunk(chunk, errors)
            processed += len(chunk)
        add_response_data("twitter", processed, errors)
    except Exception as x:
        add_response_error(x, errors)
        add_response_data("twitter", processed, errors)

    # twitter data
    telegram_settings = {
        "TELEGRAM_API_ID": settings.TELEGRAM_API_ID,
        "TELEGRAM_API_HASH": settings.TELEGRAM_API_HASH,
    }
    processed = 0
    errors = []
    try:
        messages = telegram.search_recent_telegram_messages(
            telegram_settings, start_time=start_time, end_time=end_time
        )
        for chunk in chunked(messages, INSERT_BATCH_SIZE):
            errors = insert_chunk(chunk, errors)
            processed += len(chunk)
        add_response_data("telegram", processed, errors)
    except Exception as x:
        add_response_error(x, errors)
        add_response_data("telegram", processed, errors)

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


class TagViewSet(viewsets.ModelViewSet):
    """Only allow listing tags"""

    http_method_names = ["get", "head"]
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        """Return list of strings"""
        queryset = self.get_queryset()
        data = [x.name for x in queryset]
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(data)
        return JsonResponse(data)


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

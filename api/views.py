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

# Returns a list of strings of all user permissions
def getPermissionsForUser(user):
    if user.is_superuser:
        return [str(permission) for permission in Permission.objects.all()]
    current_permissions = user.user_permissions.all() | Permission.objects.filter(
        group__user=user
    )
    return [str(permission) for permission in current_permissions]


class WhoAmIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, format=None):
        current_permissions_list = getPermissionsForUser(request.user)
        return JsonResponse(
            {
                "username": request.user.username,
                "isAuthenticated": True,
                "permissions": current_permissions_list,
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
    current_permissions_list = getPermissionsForUser(user)
    return JsonResponse(
        {
            "detail": "Successfully logged in.",
            "username": request.user.username,
            "permissions": current_permissions_list,
        }
    )


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "You're not logged in."}, status=400)

    logout(request)
    return JsonResponse({"detail": "Successfully logged out."})


class SourceViewSet(viewsets.ModelViewSet):
    """List or retrieve sources"""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [DjangoModelPermissions]


class TranslationViewSet(viewsets.ModelViewSet):
    """List or retrieve translations"""

    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

from rest_framework import viewsets
from .serializers import SourceSerializer
from .models import Source, Translation


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

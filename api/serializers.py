from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Source, Translation


class SourceSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Source
        fields = "__all__"


class TranslationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Translation
        fields = "__all__"

from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Source, Translation


class TranslationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Translation
        fields = "__all__"


class SourceSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    translations = TranslationSerializer(many=True)

    class Meta:
        model = Source
        fields = [
            "id",
            "interface",
            "source",
            "headline",
            "text",
            "language",
            "pinned",
            "timestamp",
            "tags",
            "translations",
        ]

    def create(self, validated_data):
        translations_data = validated_data.pop("translations")
        source = super().create(validated_data)
        for translation_data in translations_data:
            Translation.objects.create(source=source, **translation_data)
        return source

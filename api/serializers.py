from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Location, Source, Translation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class TranslationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Translation
        fields = ["id", "source_id", "language", "text"]


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "source_id",
            "name",
            "point",
            "polygon",
        ]


class SourceSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    translations = TranslationSerializer(many=True)
    locations = LocationSerializer(many=True)

    class Meta:
        model = Source
        fields = [
            "id",
            "interface",
            "origin",
            "external_id",
            "url",
            "media_url",
            "headline",
            "text",
            "language",
            "pinned",
            "deleted",
            "timestamp",
            "timestamp_created",
            "timestamp_updated",
            "tags",
            "translations",
            "locations",
        ]

    def create(self, validated_data):
        """Have to create translations if provided."""
        translations_data = validated_data.pop("translations")
        locations_data = validated_data.pop("locations")
        source = super().create(validated_data)
        self.create_children(source, translations_data, Translation)
        self.create_children(source, locations_data, Location)
        return source

    def update(self, instance, validated_data):
        """Have to update translations if provided."""
        translations_data = None
        locations_data = None
        if "translations" in validated_data:
            translations_data = validated_data.pop("translations") or []
        if "locations" in validated_data:
            locations_data = validated_data.pop("locations") or []
        instance = super().update(instance, validated_data)
        if translations_data is not None:
            self.update_children(
                instance, translations_data, Translation, "translations"
            )
        if locations_data is not None:
            self.update_children(instance, locations_data, Location, "locations")
        return instance

    @staticmethod
    def create_children(source, children_data, child_class):
        for child_data in children_data:
            child_class.objects.create(source=source, **child_data)

    @staticmethod
    def update_children(source, children_data, child_class, related_name):
        getattr(source, related_name).all().delete()
        new_children = [
            child_class(source=source, **child_data) for child_data in children_data
        ]
        getattr(source, related_name).set(new_children, bulk=False)

"""Serializers for the slideshows app."""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Slideshow, Slide


class SlideSerializer(serializers.ModelSerializer):
    """
    Serializer for individual slides.

    Permission-based field filtering:
    - Owner: See all fields (content, rendered_content, notes)
    - Others: Only see rendered_content (no raw content or speaker notes)
    """

    class Meta:
        model = Slide
        fields = [
            "id",
            "order",
            "content",
            "rendered_content",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "rendered_content", "created_at", "updated_at")

    def to_representation(self, instance):
        """
        Conditionally hide sensitive fields from non-owners.
        Only the slideshow owner can see raw content and notes.
        """
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request and request.user:
            # Check if user is the owner of the slideshow
            is_owner = instance.slideshow.created_by == request.user

            # Remove sensitive fields for non-owners
            if not is_owner:
                data.pop("content", None)  # Remove raw markdown
                data.pop("notes", None)  # Remove speaker notes

        return data


class SlideshowListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing slideshows.
    Does not include nested slides - only metadata.
    """

    slide_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Slideshow
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_by_username",
            "visibility",
            "language",
            "country",
            "subject",
            "is_published",
            "version",
            "slide_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_by", "version", "created_at", "updated_at")

    def get_slide_count(self, obj):
        """Return the total number of slides in this slideshow."""
        return obj.slides.count()


class SlideshowDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for slideshow detail view.
    Includes nested slides and supports partial loading via 'initial' parameter.
    """

    slides = SlideSerializer(many=True, required=False)
    slide_count = serializers.SerializerMethodField()
    remaining_slide_ids = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Slideshow
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_by_username",
            "visibility",
            "language",
            "country",
            "subject",
            "is_published",
            "version",
            "slide_count",
            "slides",
            "remaining_slide_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_slide_count(self, obj):
        """Return the total number of slides in this slideshow."""
        return obj.slides.count()

    def get_remaining_slide_ids(self, obj):
        """
        Return IDs of slides not included in the current response.
        Used for progressive loading when ?initial=N is specified.
        """
        request = self.context.get("request")
        if not request:
            return []

        # Check if initial parameter was used to limit slides
        initial_count = request.query_params.get("initial")
        if initial_count:
            try:
                initial_count = int(initial_count)
                all_slide_ids = list(
                    obj.slides.order_by("order").values_list("id", flat=True)
                )
                if len(all_slide_ids) > initial_count:
                    return all_slide_ids[initial_count:]
            except (ValueError, TypeError):
                pass

        return []

    def to_representation(self, instance):
        """
        Handle partial loading of slides via ?initial=N parameter.
        Only return first N slides if specified.
        """
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request:
            initial_count = request.query_params.get("initial")
            if initial_count:
                try:
                    initial_count = int(initial_count)
                    # Limit slides to first N
                    all_slides = instance.slides.order_by("order")[:initial_count]
                    slide_serializer = SlideSerializer(
                        all_slides, many=True, context=self.context
                    )
                    data["slides"] = slide_serializer.data
                except (ValueError, TypeError):
                    pass

        return data

    def create(self, validated_data):
        """
        Create slideshow with nested slides.
        Automatically set created_by from request user.
        """
        slides_data = validated_data.pop("slides", [])
        request = self.context.get("request")

        # Set created_by from authenticated user
        if request and request.user:
            validated_data["created_by"] = request.user

        # Create the slideshow
        slideshow = Slideshow.objects.create(**validated_data)

        # Create associated slides
        for slide_data in slides_data:
            Slide.objects.create(slideshow=slideshow, **slide_data)

        return slideshow

    def update(self, instance, validated_data):
        """
        Update slideshow and optionally update slides.
        Increment version number on successful update.
        """
        slides_data = validated_data.pop("slides", None)

        # Update slideshow fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Increment version for conflict detection
        instance.version += 1
        instance.save()

        # Update slides if provided
        if slides_data is not None:
            # Simple approach: clear existing slides and recreate
            # More sophisticated approach could handle partial updates
            instance.slides.all().delete()
            for slide_data in slides_data:
                Slide.objects.create(slideshow=instance, **slide_data)

        return instance

    def validate(self, attrs):
        """
        Validate slideshow data including version conflict detection.
        """
        # Check for version conflicts on update
        if self.instance:
            request = self.context.get("request")
            if request:
                client_version = request.data.get("version")
                if client_version is not None:
                    try:
                        client_version = int(client_version)
                        if client_version != self.instance.version:
                            raise serializers.ValidationError(
                                {
                                    "error": "version_conflict",
                                    "message": "Slideshow was modified since you loaded it",
                                    "server_version": self.instance.version,
                                    "client_version": client_version,
                                }
                            )
                    except (ValueError, TypeError):
                        pass

        return attrs

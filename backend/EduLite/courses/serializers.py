# backend/Edulite/courses/serializers.py
# Contains course serializers, course modules serializers, course membership serializers, course chatrooms serializers

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Course, CourseChatRoom, CourseMembership, CourseModule


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model.

    Includes additional derived field:
    - `duration_time`: duration of the course in minutes, calculated from start and end dates.
    """

    duration_time = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "outline",
            "language",
            "country",
            "subject",
            "visibility",
            "start_date",
            "end_date",
            "duration_time",
            "allow_join_requests",
            "is_active",
        ]
        read_only_fields = ("id", "is_active")

    def get_duration_time(self, instance):
        """
        Returns the duration of the course in minutes.
        """
        if instance.start_date and instance.end_date:
            duration = instance.end_date - instance.start_date
            return duration.total_seconds() // 60
        return 0

    def validate_title(self, value):
        """
        Ensure the title is not just whitespace.
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be all spaces.")
        return value

    def validate(self, attrs):
        """
        Ensure that start_date is not after end_date.
        """
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and start > end:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs


class CourseModuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseModule model.

    Supports:
    - `course_title`: read-only name of the related course
    - `content_type`: accepts and outputs "app_label.model" style strings
    """

    content_type = serializers.CharField()
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = CourseModule
        fields = [
            "id",
            "course",
            "title",
            "order",
            "course_title",
            "content_type",
            "object_id",
        ]
        read_only_fields = ("id",)

    def validate_content_type(self, value):
        """
        Validate content_type input as 'app_label.model' format and convert to ContentType object.
        """
        if "." not in value:
            raise serializers.ValidationError(
                "Content type must be in the format 'app_label.model'."
            )
        app_label, model = value.split(".", 1)
        try:
            return ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type.")

    def validate(self, attrs):
        """
        Validate that the referenced object_id exists under the given content_type.
        For partial updates, fall back to instance values when fields are omitted.
        """
        if isinstance(attrs.get("content_type"), str):
            attrs["content_type"] = self.validate_content_type(attrs["content_type"])

        content_type = attrs.get(
            "content_type", getattr(self.instance, "content_type", None)
        )
        object_id = attrs.get("object_id", getattr(self.instance, "object_id", None))

        # For creation, both fields are required
        if not self.instance:
            if not content_type:
                raise serializers.ValidationError(
                    {"content_type": "Content type must be provided."}
                )
            if not object_id:
                raise serializers.ValidationError(
                    {"object_id": "Object ID must be provided."}
                )

        # Validate the referenced object exists when either field is present
        if content_type and object_id:
            model_class = content_type.model_class()
            if not model_class or not model_class.objects.filter(id=object_id).exists():
                raise serializers.ValidationError(
                    {
                        "object_id": "Target object does not exist for the given content type."
                    }
                )

        return attrs

    def to_representation(self, instance):
        """
        Serialize content_type as 'app_label.model' string.
        """
        rep = super().to_representation(instance)
        rep["content_type"] = (
            f"{instance.content_type.app_label}.{instance.content_type.model}"
        )
        return rep


class CourseMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseMembership model.

    Exposes:
    - `user_name`: read-only username of the user
    - `course_title`: read-only course title
    """

    user_name = serializers.CharField(source="user.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = CourseMembership
        fields = ["id", "user", "user_name", "course", "course_title", "role", "status"]
        read_only_fields = ("id",)

    def validate(self, attrs):
        """
        Custom validation:
        - User-course pair must be unique
        - Only students can have 'pending' status
        """
        user = attrs.get("user", getattr(self.instance, "user", None))
        course = attrs.get("course", getattr(self.instance, "course", None))
        role = attrs.get("role", getattr(self.instance, "role", None))
        status = attrs.get("status", getattr(self.instance, "status", None))

        if not user or not course:
            raise serializers.ValidationError("User and course must be provided.")

        existing = CourseMembership.objects.filter(user=user, course=course)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError(
                "User is already a member of this course."
            )

        if role != "student" and status == "pending":
            raise serializers.ValidationError(
                "Only students can have 'pending' status."
            )

        return attrs


class CourseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing courses.
    Does not include nested memberships or modules - only metadata.
    """

    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "outline",
            "visibility",
            "subject",
            "language",
            "country",
            "is_active",
            "member_count",
            "is_member",
            "user_role",
            "user_status",
            "start_date",
            "end_date",
        ]
        read_only_fields = ("id", "is_active")

    def get_member_count(self, obj):
        """Return the number of enrolled members in this course."""
        if hasattr(obj, "member_count"):
            return obj.member_count
        return obj.memberships.count()

    def _get_user_membership(self, obj):
        """Return the requesting user's membership in the course, or None."""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        return obj.memberships.filter(user=request.user).first()

    def get_is_member(self, obj):
        """Return whether the requesting user is a member of this course."""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.memberships.filter(user=request.user).exists()

    def get_user_role(self, obj):
        """Return the requesting user's role in the course, or null."""
        membership = self._get_user_membership(obj)
        return membership.role if membership else None

    def get_user_status(self, obj):
        """Return the requesting user's membership status in the course, or null."""
        membership = self._get_user_membership(obj)
        return membership.status if membership else None


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for course detail view.
    Includes nested memberships, modules, and the requesting user's role.
    """

    duration_time = serializers.SerializerMethodField()
    members = CourseMembershipSerializer(
        source="memberships", many=True, read_only=True
    )
    modules = CourseModuleSerializer(source="course_modules", many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "outline",
            "language",
            "country",
            "subject",
            "visibility",
            "start_date",
            "end_date",
            "duration_time",
            "allow_join_requests",
            "is_active",
            "member_count",
            "user_role",
            "user_status",
            "members",
            "modules",
        ]
        read_only_fields = ("id", "is_active")

    def get_duration_time(self, instance):
        """Returns the duration of the course in minutes."""
        if instance.start_date and instance.end_date:
            duration = instance.end_date - instance.start_date
            return duration.total_seconds() // 60
        return 0

    def get_member_count(self, obj):
        """Return the number of enrolled members in this course."""
        if hasattr(obj, "member_count"):
            return obj.member_count
        return obj.memberships.count()

    def _get_user_membership(self, obj):
        """Return the requesting user's membership in the course, or None."""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        return obj.memberships.filter(user=request.user).first()

    def get_user_role(self, obj):
        """Return the requesting user's role in the course, or null."""
        membership = self._get_user_membership(obj)
        return membership.role if membership else None

    def get_user_status(self, obj):
        """Return the requesting user's membership status in the course, or null."""
        membership = self._get_user_membership(obj)
        return membership.status if membership else None


class CourseChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseChatRoom model.

    Exposes:
    - `course_title`: read-only course name
    - `chatroom_name`: read-only chatroom name
    - `created_user_name`: read-only creator name
    - created_by is read-only to prevent changing the creator after creation.
      To create a CourseChatRoom, set created_by to the current user in the view by using perform_create method.
    """

    course_title = serializers.CharField(source="course.title", read_only=True)
    chatroom_name = serializers.CharField(source="chatroom.name", read_only=True)
    created_user_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = CourseChatRoom
        fields = [
            "id",
            "course",
            "course_title",
            "chatroom",
            "chatroom_name",
            "created_by",
            "created_user_name",
        ]
        read_only_fields = ("id", "created_by")

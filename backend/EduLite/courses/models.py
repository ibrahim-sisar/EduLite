# backend/Edulite/courses/models.py
# Contains course models, course modules, course membership models, course chatrooms

from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from chat.models import ChatRoom
from .model_choices import (
    COUNTRY_CHOICES,
    LANGUAGE_CHOICES,
    SUBJECT_CHOICES,
    COURSE_VISIBILITY_CHOICES,
    COURSE_ROLE_CHOICES,
    COURSE_MEMBERSHIP_STATUS,
)

User = get_user_model()


class Course(models.Model):
    """
    A course is a collection of modules that are taught by a teacher to a group of students.
    which can be public, private, or restricted.
    """

    title = models.CharField(
        blank=False,
        null=False,
        max_length=128,
        help_text="What your Course is called..",
    )
    outline = models.TextField(
        blank=True,
        null=True,
        max_length=1000,
        help_text="A brief description of the course.",
    )

    language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    country = models.CharField(
        max_length=64, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    subject = models.CharField(
        max_length=64, choices=SUBJECT_CHOICES, blank=True, null=True
    )

    # the visibility choices include: public, private, restricted
    visibility = models.CharField(
        max_length=64, choices=COURSE_VISIBILITY_CHOICES, null=False, default="private"
    )

    # the start and end date are the dates when the course is available to students
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(
        default=datetime(2099, 12, 31, 23, 59, 59),  # default to a far future date
        blank=True,
        null=True,
    )

    # the is_active flag is used to indicate if the course is currently active
    is_active = models.BooleanField(default=False)

    # the allow_join_requests flag is used to indicate if the course allows join requests
    allow_join_requests = models.BooleanField(default=False)

    def clean(self) -> None:
        super().clean()

        # Checking course start date should be before end date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")
        # Title should not be all spaces
        if not self.title.strip():
            raise ValidationError("Title cannot be all spaces")

    def __str__(self) -> str:
        return self.title


class CourseModule(models.Model):
    """
    Represents a modular unit within a Course. Each module can be dynamically linked
    to different types of content such as lectures, quizzes, assignments, etc.

    This flexible structure is implemented using Django's GenericForeignKey, which
    allows associating the module with any content type (model) instance dynamically.

    Reference:
    Django Documentation – Content types framework
    https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/
    """

    course = models.ForeignKey(
        Course, related_name="course_modules", on_delete=models.CASCADE
    )
    # the title of the module
    title = models.CharField(
        max_length=128, blank=True, null=True, help_text="What your Module is called."
    )

    # Display order of the module within the course
    order = models.PositiveIntegerField(
        default=0,
        help_text="The order of the module within the course's list of modules.",
    )

    # the content_type and object_id are used to link the module to a specific content object
    # example: Lecture, Quiz, Assignment, etc.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="course_contents",
        help_text="The type of the content object",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # the index is used to speed up the lookup of the content_object
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def clean(self) -> None:
        super().clean()

        # Checking if the content_type and object_id are valid
        if not self.content_type_id or not self.object_id:
            raise ValidationError("Content type and object id are required")
        # Checking content_object is exist
        try:
            if not self.content_object:
                raise ValidationError("Content object does not exist")
        except self.content_type.model_class().DoesNotExist:
            raise ValidationError("Content object does not exist")

    def __str__(self):
        if self.title:
            return f"{self.course.title} - {self.title}"
        else:
            return f"{self.course.title} - module {self.order}"


class CourseMembership(models.Model):
    """
    Represents a user's membership in a course.
    A user can have multiple memberships in a course, each with a different role.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_memberships",
        help_text="The user who is a member of the course.",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text="The course that the user is a member of.",
    )
    role = models.CharField(
        max_length=32,
        choices=COURSE_ROLE_CHOICES,
        default="student",
        help_text="The role of the user in the course. (student, assistant, teacher)",
    )
    status = models.CharField(
        max_length=64,
        choices=COURSE_MEMBERSHIP_STATUS,
        default="enrolled",
        help_text="The status of the user in the course. (pending, enrolled, invited)",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_user_course_membership"
            )
        ]

    def clean(self) -> None:
        super().clean()

        # Checking if the user is already a member of the course
        if (
            CourseMembership.objects.filter(user=self.user, course=self.course)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("User is already a member of the course")

        # Checking state match the role
        if self.role != "student" and self.status == "pending":
            raise ValidationError("Only students can have 'pending' status.")

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.role}"


class CourseChatRoom(models.Model):
    """
    Represents a chatroom associated with a course.
    This allows for a multiple chatrooms to be shared across single course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_chatrooms",
        help_text="The course that the chatroom is associated with.",
    )
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="course_links",
        help_text="The chatroom that is associated with the course.",
    )
    created_by = models.ForeignKey(
        User,
        related_name="chatroom_user",
        on_delete=models.CASCADE,
        help_text="The user who created the chatroom.",
    )

    def __str__(self):
        return f"{self.course.title} - {self.chatroom.name}"

    def clean(self):
        super().clean()
        # Ensure that created user cannot be changed.
        if self.pk:
            old_instance = CourseChatRoom.objects.get(pk=self.pk)

            if old_instance.created_by != self.created_by:
                raise ValidationError("Cannot change the creator of the chatroom.")

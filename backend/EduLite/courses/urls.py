from django.urls import path

from .views import (
    CourseDetailView,
    CourseEnrollView,
    CourseListCreateView,
    CourseMembershipDetailView,
    CourseMembershipListInviteView,
    CourseModuleDetailView,
    CourseModuleListCreateView,
)

urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "courses/<int:pk>/modules/",
        CourseModuleListCreateView.as_view(),
        name="course-module-list-create",
    ),
    path(
        "courses/<int:pk>/modules/<int:module_id>/",
        CourseModuleDetailView.as_view(),
        name="course-module-detail",
    ),
    path(
        "courses/<int:pk>/members/",
        CourseMembershipListInviteView.as_view(),
        name="course-membership-list-invite",
    ),
    path(
        "courses/<int:pk>/members/<int:membership_id>/",
        CourseMembershipDetailView.as_view(),
        name="course-membership-detail",
    ),
    path(
        "courses/<int:pk>/enroll/",
        CourseEnrollView.as_view(),
        name="course-enroll",
    ),
]

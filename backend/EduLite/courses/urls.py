from django.urls import path

from .views import CourseCreateView, CourseModuleDetailView, CourseModuleListCreateView

urlpatterns = [
    path("courses/", CourseCreateView.as_view(), name="course-create"),
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
]

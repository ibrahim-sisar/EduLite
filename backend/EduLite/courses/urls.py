from django.urls import path

from .views import CourseCreateView

urlpatterns = [
    path("courses/", CourseCreateView.as_view(), name="course-create"),
]

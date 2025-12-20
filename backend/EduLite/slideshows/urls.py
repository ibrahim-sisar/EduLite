"""URL patterns for the slideshows app."""

from django.urls import path
from .views import (
    SlideshowListCreateView,
    SlideshowRetrieveUpdateDestroyView,
    SlideCreateView,
    SlideRetrieveUpdateDestroyView,
)

app_name = "slideshows"

urlpatterns = [
    # Slideshow list and create
    path("", SlideshowListCreateView.as_view(), name="slideshow-list-create"),
    # Slideshow detail, update, delete
    path(
        "<int:pk>/",
        SlideshowRetrieveUpdateDestroyView.as_view(),
        name="slideshow-detail",
    ),
    # Create slide in slideshow
    path(
        "<int:pk>/slides/",
        SlideCreateView.as_view(),
        name="slide-create",
    ),
    # Individual slide retrieve, update, delete
    path(
        "<int:pk>/slides/<int:slide_id>/",
        SlideRetrieveUpdateDestroyView.as_view(),
        name="slide-detail",
    ),
]

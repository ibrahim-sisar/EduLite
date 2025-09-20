from django.urls import path
from .views import NotesListCreateView, NotesDetailView, DownloadNoteFilesView
urlpatterns = [
    path("notes/", NotesListCreateView.as_view(), name="note_list_create"),
    path("notes/<int:note_id>/download/", DownloadNoteFilesView.as_view(), name="download_note_files"),
    path("notes/<int:pk>/", NotesDetailView.as_view(), name="note_detail"),
]

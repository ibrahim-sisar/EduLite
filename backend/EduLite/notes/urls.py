from django.urls import path
from .views import NotesListCreateView, NotesDeatilView, download_note_files

urlpatterns = [
    path("notes/", NotesListCreateView.as_view(), name="note_list_create"),
    path("notes/<int:note_id>/download/", download_note_files, name="download_note_files"),
    path("notes/<int:pk>/", NotesDeatilView.as_view(), name="note_detail"),
]

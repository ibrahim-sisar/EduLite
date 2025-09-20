from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notes, NotesFiles
from .serializers import NotesSerializer, NotesCreateSerializer
from .permissions import IsOwnerOrReadOnly
from download_zip_logic import prepare_note_files_response

# Create your views here.
class NotesListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing all notes or creating a new note.

    - GET: Returns a list of all notes (with files).
    - POST: Creates a new note and associates uploaded files with it.

    Uses:
    - NoteSerializer for GET requests.
    - NoteCreateSerializer for POST requests.
    """

    queryset = Notes.objects.all().order_by("uploaded_at")
    #permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return different serializers for GET vs POST requests."""
        if self.request.method == "POST":
            return NotesCreateSerializer
        return NotesSerializer
    
    def perform_create(self, serializer):
        """Save note with the logged-in user as uploader."""
        serializer.save(uploader=self.request.user)

class NotesDeatilView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a single note.

    - GET: Retrieve a specific note and its files.
    - PATCH/PUT: Update the note (only allowed for owner).
    - DELETE: Remove the note (only allowed for owner).

    Permissions:
    - IsAuthenticated: user must be logged in.
    - IsOwnerOrReadOnly: only the owner can edit or delete.
    """
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class DownloadNoteFilesView(APIView):
    """
    Download all files for a specific note.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, note_id):
        note = get_object_or_404(Notes, id=note_id)
        files = note.files.all()

        if not files.exists():
            return Response({"error": "No files found for this note"}, status=404)
        # prepare_note_files_response provides zip logic
        return prepare_note_files_response(note, files)
    

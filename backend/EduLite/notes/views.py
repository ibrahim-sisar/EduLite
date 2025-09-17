from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import zipfile, os
from io import BytesIO
from .models import Notes, NotesFiles
from .serializers import NotesSerializer, NotesCreateSerializer
from .permissions import IsOwnerOrReadOnly

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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def download_note_files(request, note_id):
    """
    Download all files for a specific note.
    - If the note has 1 file → return the file directly.
    - If multiple files → compress into a ZIP archive and return.

    Args:
        request: the HTTP request object
        note_id: the ID of the Note whose files should be downloaded

    Returns:
        HttpResponse: single file or ZIP file for download
    """
    note = get_object_or_404(Notes, id=note_id)
    files = note.files.all()

    if not files.exists():
        return Response({"error": "No files found for this note"}, status=404)

    if files.count() == 1:
        file_obj = files.first().file
        response = HttpResponse(file_obj, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_obj.name)}"'
        return response

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        for file in files:
            zipf.write(file.file.path, os.path.basename(file.file.name))
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{note.title}_files.zip"'
    return response
    

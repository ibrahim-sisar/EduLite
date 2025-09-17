from rest_framework import serializers
from .models import Notes, NotesFiles

class NotesFilesSerializer(serializers.ModelSerializer):
    """
    Serializer for NoteFile model.
    Represents a single uploaded file belonging to a Note.
    Used for returning file details such as ID, file path, and upload time.
    """

    class Meta:
        model = NotesFiles
        fields = ["id", "files", "uploaded_at"]

class NotesSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Note model.
    Includes nested NoteFileSerializer to display all attached files.
    Used for GET requests when listing or retrieving notes.
    """

    files = NotesFilesSerializer(many=True, read_only=True)
    class Meta:
        model = Notes
        fields = [
            "id",
            "level",
            "subject",
            "course",
            "title",
            "description",
            "uploader",
            "uploaded_at",
            "files",
        ]
        read_only_fields = ["uploader", "uploaded_at"]
        
class NotesCreateSerializer(serializers.ModelSerializer):
    """
    Write-only serializer for creating Note objects with file uploads.
    Allows multiple files to be uploaded at once using a ListField.
    """

    files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Notes
        fields = [
            "id",
            "level",
            "subject",
            "course",
            "title",
            "description",
            "files",
        ]

    def create(self, validated_data):
        """
        Create a Note and associate uploaded files with it.
        - Extracts files from validated_data.
        - Saves Note with the current user as uploader
        - Iterates through uploaded files and creates NoteFile entries.
        """
        files = validated_data.pop("files", [])
        note = Notes.objects.create(**validated_data)
        for f in files:
            NotesFiles.objects.create(note=note, files=f)
        return note
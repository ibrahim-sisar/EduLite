import io
import uuid
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Notes, NotesFiles

User = get_user_model()

def get_unique_username(base="user"):
    return f"{base}_{uuid.uuid4().hex[:6]}"

class NoteFeatureTests(APITestCase):

    def setUp(self):
        # Create test user and JWT token
        self.user = User.objects.create_user(
            username=get_unique_username("testuser"),
            password="password123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create a note for testing detail & permissions
        self.note = Notes.objects.create(
            uploader=self.user,
            title="Sample Note",
            level="high_school",
            subject="math",
            course="algebra",
            description="Sample description",
        )

    def test_create_note_with_files(self):
        url = reverse("note_list_create")  # Update with your URL name
        file1 = SimpleUploadedFile("file0.txt", b"File content 0")
        file2 = SimpleUploadedFile("file1.txt", b"File content 1")

        data = {
            "title": "New Note",
            "level": "high_school",   # Use choice values
            "subject": "math",        # Use choice values
            "course": "algebra",
            "description": "Test description",
            "files": [file1, file2],
        }

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check files were attached
        note_id = response.data["id"]
        note = Notes.objects.get(id=note_id)
        self.assertEqual(note.files.count(), 2)

    def test_download_multiple_files_zips(self):
        # Attach files to note
        file1 = NotesFiles.objects.create(
            note=self.note,
            files=SimpleUploadedFile("file0.txt", b"File content 0")
        )
        file2 = NotesFiles.objects.create(
            note=self.note,
            files=SimpleUploadedFile("file1.txt", b"File content 1")
        )

        url = reverse("download_note_files", args=[self.note.id])  # Update URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/zip')

    def test_get_note_detail(self):
        url = reverse("note_detail", args=[self.note.id])  # Update URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.note.title)

    def test_permission_update_note(self):
        # Create another user with unique username
        other_user = User.objects.create_user(
            username=get_unique_username("otheruser"),
            password="pass123"
        )
        refresh = RefreshToken.for_user(other_user)
        other_token = str(refresh.access_token)

        # Authenticate as other user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_token}")

        url = reverse("note_detail", args=[self.note.id])  # Update URL
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
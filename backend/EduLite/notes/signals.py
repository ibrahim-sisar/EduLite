import os
import threading
from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import pikepdf
from .models import NoteFile

def compress_file_on_upload_logic(instance):
    """
    Actual compression logic separated from signal.
    Can be run in background thread to avoid blocking user request.
    """

    file_path = instance.file.path
    ext = os.path.splitext(file_path)[1].lower()

    # Compress images
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            img = Image.open(file_path)
            img_io = BytesIO()

            # Save with reduced quality
            if ext in [".jpg", ".jpeg"]:
                img.save(img_io, format="JPEG", optimize=True, quality=90)  # good balance
            elif ext == ".png":
                img.save(img_io, format="PNG", optimize=True)  # lossless

            # Overwrite original file
            with open(file_path, "wb") as f:
                f.write(img_io.getvalue())

            print(f"Compressed image: {file_path}")

        except Exception as e:
            print(f"Image compression failed: {e}")

    # Compress PDFs
    elif ext == ".pdf":
        try:
            output_path = file_path  # overwrite original file
            with pikepdf.open(file_path) as pdf:
                pdf.save(
                    output_path,
                    optimize_streams=True,   # remove unused objects
                    compress_streams=True    # compress content streams
                )
            print(f"Compressed PDF: {file_path}")
        except Exception as e:
            print(f"PDF compression failed: {e}")

    # Other files (DOCX, XLSX, TXT) → skip
    else:
        print(f"No compression applied for: {file_path}")

@receiver(post_save, sender=NoteFile)
def compress_file_on_upload(sender, instance, **kwargs):
    """
    Signal: triggered after a NoteFile is saved.
    Runs compression in a background thread to avoid blocking the request.
    """
    thread = threading.Thread(target=compress_file_on_upload_logic, args=(instance,))
    thread.start()
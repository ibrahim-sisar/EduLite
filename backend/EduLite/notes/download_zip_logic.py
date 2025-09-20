import os
import zipfile
from io import BytesIO
from django.http import HttpResponse


def prepare_note_files_response(note, files):
    """
    Prepares an HttpResponse to download note files.
    - If the note has 1 file → return the file directly.
    - If multiple files → compress into a ZIP archive and return.
    """
    # Case 1: single file
    if files.count() == 1:
        file_obj = files.first().file
        response = HttpResponse(file_obj, content_type="application/octet-stream")
        response["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(file_obj.name)}"'
        )
        return response

    # Case 2: multiple files → ZIP
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        for file in files:
            zipf.write(file.file.path, os.path.basename(file.file.name))
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = (
        f'attachment; filename="{note.title}_files.zip"'
    )
    return response
"""infrastructure/storage/file_storage.py — File upload, storage and retrieval."""
import os
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

# Allowed MIME types for uploads.
# "application/octet-stream" is included because some browsers and HTTP clients
# (especially non-specialised DICOM viewers) send DICOM files with this generic
# type instead of "application/dicom". Without it, DICOM uploads are rejected.
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/dicom",
    "application/octet-stream",   # FIX: required for DICOM from generic HTTP clients
    "text/plain",
    "text/csv",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class UploadedFile(models.Model):
    """Database record for every uploaded file.

    The file itself lives on disk under MEDIA_ROOT/<folder>/<uuid><ext>.
    This record tracks metadata and links the file to a clinical entity.
    app_label="authentication" means the migration lives in authentication/migrations/.
    """
    original_name = models.CharField(max_length=255)
    file_name     = models.CharField(max_length=255)
    file_path     = models.CharField(max_length=500)
    content_type  = models.CharField(max_length=100)
    size_bytes    = models.PositiveIntegerField()
    folder        = models.CharField(max_length=100, db_index=True)
    entity_type   = models.CharField(max_length=100, null=True, blank=True)
    entity_id     = models.CharField(max_length=50,  null=True, blank=True)
    uploaded_by   = models.CharField(max_length=50)
    uploaded_at   = models.DateTimeField()

    class Meta:
        app_label = "authentication"
        db_table  = "files"
        indexes   = [
            models.Index(fields=["entity_type", "entity_id"], name="ix_files_entity"),
            models.Index(fields=["folder"],                    name="ix_files_folder"),
            models.Index(fields=["uploaded_by"],               name="ix_files_uploader"),
        ]

    def __str__(self):
        return f"{self.original_name} ({self.folder}/{self.file_name})"


class FileStorageService:
    """Handles file save, URL generation, and deletion."""

    def save(self, uploaded_file, folder: str, entity_type: str = None,
             entity_id: str = None, uploaded_by: str = "system") -> UploadedFile:
        """Save an uploaded file to disk and create a database record.

        Raises ValueError for disallowed types or files that are too large.
        """
        if uploaded_file.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"File type '{uploaded_file.content_type}' is not allowed. "
                f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            )
        if uploaded_file.size > MAX_FILE_SIZE:
            raise ValueError(
                f"File is too large ({uploaded_file.size / 1024 / 1024:.1f} MB). "
                f"Maximum allowed size is 50 MB."
            )

        ext       = os.path.splitext(uploaded_file.name)[1].lower()
        file_name = f"{uuid.uuid4()}{ext}"
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return UploadedFile.objects.create(
            original_name=uploaded_file.name,
            file_name=file_name,
            file_path=file_path,
            content_type=uploaded_file.content_type,
            size_bytes=uploaded_file.size,
            folder=folder,
            entity_type=entity_type,
            entity_id=entity_id,
            uploaded_by=uploaded_by,
            uploaded_at=timezone.now(),
        )

    def get_url(self, file_path: str) -> str:
        """Return the public URL for a stored file path."""
        rel = os.path.relpath(file_path, settings.MEDIA_ROOT)
        # os.path.relpath uses os.sep (backslash on Windows).
        # This code runs in Docker (Linux) so sep is always '/', but normalize anyway.
        return settings.MEDIA_URL + rel.replace(os.sep, "/")

    def delete_file(self, file_path: str) -> None:
        """Delete a file from disk. Does NOT delete the database record.

        The caller (FileDetailView.delete) is responsible for deleting the
        UploadedFile record from the database. Both steps should be called
        together — see FileDetailView for the correct pattern.
        """
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            log_msg = f"Deleted file from disk: {file_path}"
        else:
            log_msg = f"delete_file called but file not found on disk: {file_path}"

        import logging
        logging.getLogger("virtual_hospital").debug(log_msg)
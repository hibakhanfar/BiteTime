from django.db import models
from . import User


class PresignedUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        EXPIRED = "EXPIRED", "Expired"

    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="presigned_uploads"
    )
    object_key = models.CharField(max_length=500, unique=True)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.object_key} ({self.status})"

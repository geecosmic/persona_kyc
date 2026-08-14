from django.conf import settings
from django.db import models
from django.utils import timezone

class PersonaInquiry(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CREATED = "created", "Created"
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        NEEDS_REVIEW = "needs_review", "Needs Review"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="persona_inquiries",
    )
    inquiry_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    reference_id = models.CharField(max_length=128, db_index=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.reference_id} → {self.status}"
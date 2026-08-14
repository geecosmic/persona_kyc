from django.conf import settings
from .models import PersonaInquiry

def get_or_create_inquiry(user) -> PersonaInquiry:
    """
    Returns the latest pending/created inquiry for the user,
    or creates a new one.
    """
    inquiry = (
        PersonaInquiry.objects
        .filter(user=user, status__in=["pending", "created", "started"])
        .order_by("-created_at")
        .first()
    )
    if inquiry:
        return inquiry

    return PersonaInquiry.objects.create(
        user=user,
        reference_id=str(user.pk),  # or user.uuid / custom ID
        status=PersonaInquiry.Status.PENDING,
    )
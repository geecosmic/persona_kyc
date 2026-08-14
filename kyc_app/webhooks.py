  
  
# persona_kyc/webhooks.py
import hmac
import hashlib
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import PersonaInquiry

def verify_signature(request) -> bool:
    signature_header = request.headers.get("Persona-Signature")
    if not signature_header:
        return False

    try:
        parts = dict(item.split("=") for item in signature_header.split(","))
        t = parts.get("t")
        v1 = parts.get("v1")
    except Exception:
        return False

    if not t or not v1:
        return False

    payload = f"{t}.{request.body.decode('utf-8')}"
    expected = hmac.new(
        settings.PERSONA_WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)

@csrf_exempt
@require_POST
def persona_webhook(request):
    if not verify_signature(request):
        return HttpResponseBadRequest("Invalid signature")

    try:
        data = json.loads(request.body)
        event_name = data["data"]["attributes"]["name"]
        payload = data["data"]["attributes"]["payload"]["data"]
    except (KeyError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid payload")

    inquiry_id = payload.get("id")
    attributes = payload.get("attributes", {})
    status = attributes.get("status")
    reference_id = attributes.get("reference-id")

    if not inquiry_id:
        return HttpResponse(status=200)

    # Map Persona statuses
    status_map = {
        "created": PersonaInquiry.Status.CREATED,
        "pending": PersonaInquiry.Status.PENDING,
        "completed": PersonaInquiry.Status.COMPLETED,
        "approved": PersonaInquiry.Status.APPROVED,
        "declined": PersonaInquiry.Status.DECLINED,
        "failed": PersonaInquiry.Status.FAILED,
        "expired": PersonaInquiry.Status.EXPIRED,
        "needs_review": PersonaInquiry.Status.NEEDS_REVIEW,
    }

    mapped_status = status_map.get(status, status)

    inquiry, created = PersonaInquiry.objects.update_or_create(
        inquiry_id=inquiry_id,
        defaults={
            "status": mapped_status,
            "reference_id": reference_id or "",
            "raw_payload": data,
            "completed_at": timezone.now() if status in ("approved", "declined", "failed", "completed") else None,
        },
    )

    # Optional: also update user profile flag
    # if mapped_status == PersonaInquiry.Status.APPROVED:
    #     inquiry.user.profile.is_verified = True
    #     inquiry.user.profile.save()

    return HttpResponse(status=200)  
  
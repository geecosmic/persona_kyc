from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from .models import PersonaInquiry
from .services import get_or_create_inquiry

@login_required
@require_GET
def verify_identity(request):
    inquiry = get_or_create_inquiry(request.user)

    context = {
        "kyc_status": inquiry.status.upper(),
        "template_id": settings.PERSONA_TEMPLATE_ID,
        "environment_id": settings.PERSONA_ENVIRONMENT_ID,
        "reference_id": inquiry.reference_id,
        "sdk_version": getattr(settings, "PERSONA_SDK_VERSION", "5.8.0"),
    }
    return render(request, "persona_kyc/verify.html", context)
  
  
 def ping(request):
    return HttpResponseBadRequest("ok")  
  
  
   
  
  
  

from django.urls import path
from . import views
from .webhooks import persona_webhook
from django.contrib.auth import views as auth_views


app_name = "persona_kyc"

urlpatterns = [
    path("", views.verify_identity, name="verify"),
    path("webhook/", persona_webhook, name="webhook"),

    path("ping/", views.ping, name="ping"),
    
]

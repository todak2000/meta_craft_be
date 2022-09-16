from pathlib import Path
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("auth", views.test_auth),
    path("signup", views.signup),
    path("verify-user", views.verify),
    path("resend-code", views.resend_code),
]

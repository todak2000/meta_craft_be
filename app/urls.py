from pathlib import Path
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("auth", views.test_auth),
    path("signup", views.signup),
    path("signin", views.signin),
    path("verify-user", views.verify),
    path("resend-code", views.resend_code),
    path("forgot-password", views.forgot_password),
    path("change-password", views.change_password),
    path("get-sp", views.get_sp),
]

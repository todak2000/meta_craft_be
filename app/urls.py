from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("auth", views.test_auth),
    path("signup", views.signup),
]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="predictor"),
    path("api/generate/", views.api_generate, name="predictor_api_generate"),
]
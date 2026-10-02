from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="analytics"),
    path("api/", views.api_analytics, name="analytics_api"),
]
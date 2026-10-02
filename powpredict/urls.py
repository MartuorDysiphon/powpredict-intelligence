from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("",           include("dashboard.urls")),
    path("predictor/", include("predictor.urls")),
    path("results/",   include("results.urls")),
    path("analytics/", include("analytics.urls")),
    path("history/",   include("history.urls")),
]
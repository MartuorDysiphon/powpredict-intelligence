from django.shortcuts import render
from core.nav import set_active


def index(request):
    set_active(request, "history")
    return render(request, "history/index.html")
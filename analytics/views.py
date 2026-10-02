from django.shortcuts import render
from django.http import JsonResponse

from core.nav import set_active

from .services import (
    GAME_LABELS,
    hot_numbers,
    cold_numbers,
    frequency_distribution,
    WINDOW,
)


def index(request):
    set_active(request, "analytics")

    game = request.GET.get("game", "lotto")
    if game not in GAME_LABELS:
        game = "lotto"

    return render(request, "analytics/index.html", {
        "game": game,
        "game_label": GAME_LABELS[game],
        "games": GAME_LABELS,
        "window": WINDOW,
        "hot": hot_numbers(game),
        "cold": cold_numbers(game),
        "freq": frequency_distribution(game),
    })


def api_analytics(request):
    """JSON endpoint so the game selector can fetch fresh data via AJAX."""
    game = request.GET.get("game", "lotto")
    if game not in GAME_LABELS:
        game = "lotto"

    return JsonResponse({
        "game": game,
        "label": GAME_LABELS[game],
        "window": WINDOW,
        "hot": hot_numbers(game),
        "cold": cold_numbers(game),
        "freq": frequency_distribution(game),
    })
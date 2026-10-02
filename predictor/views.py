from django.http import JsonResponse
from django.shortcuts import render

from core.nav import set_active

from .analysis import build_profile, summarize_profile, GAMES_FOR_ANALYSIS
from .engine import generate_best_set
from .weather import get_weather


def index(request):
    set_active(request, "predictor")

    game = request.GET.get("game", "lotto")
    if game not in GAMES_FOR_ANALYSIS:
        game = "lotto"

    profile = build_profile(game)
    summary = summarize_profile(profile) if profile else None

    weather = get_weather()

    return render(request, "predictor/index.html", {
        "game": game,
        "game_label": GAMES_FOR_ANALYSIS[game],
        "games": GAMES_FOR_ANALYSIS,
        "summary": summary,
        "weather": weather,
        "sample_size": profile["total_draws"] if profile else 0,
    })


def api_generate(request):
    game = request.GET.get("game", "lotto")
    if game not in GAMES_FOR_ANALYSIS:
        game = "lotto"

    weighted = request.GET.get("weighted", "1") != "0"
    avoid_raw = request.GET.get("avoid", "")
    avoid = [int(n) for n in avoid_raw.split(",") if n.strip().isdigit()] if avoid_raw else []

    mains, bonus, meta = generate_best_set(game, weighted=weighted, avoid=avoid)

    return JsonResponse({
        "game": game,
        "mains": mains,
        "bonus": bonus,
        "score": meta.get("score", 0),
        "sample_size": meta.get("sample_size", 0),
    })
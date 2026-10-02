from datetime import date

from django.shortcuts import render

from core.nav import set_active
from results.models import DrawResult
from analytics.services import (
    GAME_LABELS,
    hot_numbers,
    cold_numbers,
)


def index(request):
    set_active(request, "dashboard")

    # Default game for the dashboard cards
    game = "lotto"
    game_label = GAME_LABELS[game]

    # Hot / cold from the real DB
    hot = hot_numbers(game, limit=6)
    cold = cold_numbers(game, limit=6)

    # Total draws in DB
    total_draws = DrawResult.objects.count()

    # Latest draws per game for the mini-summary
    latest_per_game = []
    for key, label in GAME_LABELS.items():
        latest = DrawResult.objects.filter(game=key).order_by("-draw_date").first()
        latest_per_game.append({
            "game": key,
            "label": label,
            "latest": latest,
        })

    # Recent predictions (from DrawResult — the newest draws in the DB)
    recent_draws = DrawResult.objects.order_by("-draw_date")[:8]

    # Compute odd/even and low/high for the most recent Lotto draw
    latest_lotto = DrawResult.objects.filter(game="lotto").order_by("-draw_date").first()
    oe_stats = None
    lh_stats = None
    if latest_lotto:
        mains = latest_lotto.mains
        total = len(mains)
        odd = sum(1 for n in mains if n % 2)
        even = total - odd
        half = 26  # Lotto max is 52
        lows = sum(1 for n in mains if n <= half)
        highs = total - lows
        oe_stats = {
            "odd": odd,
            "even": even,
            "odd_pct": round(odd / total * 100) if total else 0,
            "even_pct": round(even / total * 100) if total else 0,
        }
        lh_stats = {
            "lows": lows,
            "highs": highs,
            "low_pct": round(lows / total * 100) if total else 0,
            "high_pct": round(highs / total * 100) if total else 0,
        }

    return render(request, "dashboard/index.html", {
        "game": game,
        "game_label": game_label,
        "hot": hot,
        "cold": cold,
        "total_draws": total_draws,
        "latest_per_game": latest_per_game,
        "recent_draws": recent_draws,
        "latest_lotto": latest_lotto,
        "oe_stats": oe_stats,
        "lh_stats": lh_stats,
    })
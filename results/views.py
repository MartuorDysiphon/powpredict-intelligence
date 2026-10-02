from datetime import timedelta

from django.core.management import call_command
from django.shortcuts import render
from django.utils import timezone

from core.nav import set_active
from .models import DrawResult


STALE_AFTER = timedelta(hours=6)

GAME_LABELS = {
    "lotto":          "Lotto",
    "lotto-plus-1":   "Lotto Plus 1",
    "lotto-plus-2":   "Lotto Plus 2",
    "powerball":      "PowerBall",
    "powerball-plus": "PowerBall Plus",
    "daily":          "Daily Lotto",
}


def index(request):
    set_active(request, "results")

    # Refresh from the web if the newest scrape is stale.
    newest = DrawResult.objects.order_by("-scraped_at").first()
    if not newest or (timezone.now() - newest.scraped_at) > STALE_AFTER:
        try:
            call_command("scrape_results")   # default window: current + last 4 years
        except Exception:
            pass  # don't break the page if scraping fails

    sections = []
    for key, label in GAME_LABELS.items():
        draws = DrawResult.objects.filter(game=key).order_by("-draw_date")
        sections.append({
            "game": key,
            "label": label,
            "count": draws.count(),
            "draws": draws,
        })

    return render(request, "results/index.html", {
        "sections": sections,
        "updated": timezone.localtime().strftime("%H:%M:%S"),
    })